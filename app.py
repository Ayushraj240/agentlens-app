import os
import json
from flask import Flask, render_template, request, jsonify
from shopify_fetcher import get_products
from analyzer import analyze_products
from agent import RecommendationAgent, AutoOptimizingAgent, ChatbotOptimizerAgent, MarketingCopyAgent, CompetitorAnalysisAgent, RepresentationLabAgent
from dotenv import load_dotenv

# Load local environment variables from .env if present
load_dotenv()

app = Flask(__name__)

import os
# Check if running on Vercel (Vercel sets specific environment variables)
if os.environ.get("VERCEL") or os.environ.get("VERCEL_URL"):
    DB_FILE = "/tmp/simulated_products.json"
else:
    DB_FILE = "simulated_products.json"

def load_simulated_products():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_simulated_products(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving simulated database: {e}")

def get_cached_products():
    products = get_products()
    sim_db = load_simulated_products()
    for p in products:
        pid = str(p.get("id"))
        if pid in sim_db:
            # Overwrite with simulated content
            p.update(sim_db[pid])
    return products

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route("/")
def home():
    products = get_cached_products()
    report, avg_score = analyze_products(products)

    # Sort report by score ascending (lowest score/Poor first)
    report_sorted = sorted(report, key=lambda x: x.get("score", 0))

    return render_template(
        "index.html",
        report=report_sorted,
        avg_score=round(avg_score, 2)
    )

@app.route("/api/recommend/<product_id>", methods=["GET"])
def recommend_endpoint(product_id):
    products = get_cached_products()
    product = None
    for p in products:
        if str(p.get("id")) == str(product_id):
            product = p
            break
            
    if not product:
        return jsonify({"error": "Product not found"}), 404
        
    # Analyze to get current issues
    single_report, _ = analyze_products([product])
    issues = single_report[0].get("issues", [])
    
    recommendations = RecommendationAgent.get_recommendations(product, issues)
    recommendations["current_score"] = single_report[0].get("score")
    recommendations["original_description"] = product.get("body_html", "") or ""
    recommendations["categorized_issues"] = single_report[0].get("categorized_issues", {"high": [], "medium": [], "low": []})
    
    # Generate the optimized content to show side-by-side what it would look like
    optimized = AutoOptimizingAgent.generate_optimized_content(product, issues)
    recommendations["optimized_description"] = optimized.get("new_description", "") or ""
    
    return jsonify(recommendations)

@app.route("/api/optimize/<product_id>", methods=["POST"])
def optimize_endpoint(product_id):
    products = get_cached_products()
    product = None
    for p in products:
        if str(p.get("id")) == str(product_id):
            product = p
            break
            
    if not product:
        return jsonify({"error": "Product not found"}), 404
        
    single_report, _ = analyze_products([product])
    issues = single_report[0].get("issues", [])
    
    result = AutoOptimizingAgent.optimize_product(product, issues)
    
    if result.get("success"):
        # Re-fetch or re-analyze the updated product to return the new score and issues
        updated_product = result.get("product")
        
        # Save to simulated cache to persist updates locally
        sim_db = load_simulated_products()
        sim_db[str(product_id)] = updated_product
        save_simulated_products(sim_db)
        
        new_report, _ = analyze_products([updated_product])
        
        return jsonify({
            "success": True,
            "new_score": new_report[0].get("score"),
            "new_issues": new_report[0].get("issues"),
            "changes": result.get("changes"),
            "demo_mode": result.get("demo_mode", False),
            "new_image_url": new_report[0].get("image_url")
        })
    else:
        return jsonify({
            "success": False,
            "error": result.get("error", "Unknown optimization error")
        }), 500

@app.route("/api/representation-lab/<product_id>", methods=["GET"])
def representation_lab_endpoint(product_id):
    products = get_cached_products()
    product = None
    for p in products:
        if str(p.get("id")) == str(product_id):
            product = p
            break
            
    if not product:
        return jsonify({"error": "Product not found"}), 404
        
    single_report, _ = analyze_products([product])
    issues = single_report[0].get("issues", [])
    
    result = RepresentationLabAgent.generate_lab_analysis(product, issues)
    return jsonify(result)

@app.route("/api/chat", methods=["POST"])
def chat_endpoint():
    data = request.get_json() or {}
    message = data.get("message", "")
    history = data.get("history", [])
    
    # Get all products context
    products = get_cached_products()
    report, _ = analyze_products(products)
    
    response_text = ChatbotOptimizerAgent.get_chat_response(message, history, report)
    return jsonify({"response": response_text})

@app.route("/api/batch-optimize", methods=["POST"])
def batch_optimize_endpoint():
    data = request.get_json() or {}
    product_ids = data.get("product_ids", [])
    if not product_ids:
        return jsonify({"error": "No product IDs provided"}), 400
        
    products = get_cached_products()
    results = {}
    
    for pid in product_ids:
        product = None
        for p in products:
            if str(p.get("id")) == str(pid):
                product = p
                break
        if not product:
            results[pid] = {"success": False, "error": "Product not found"}
            continue
            
        try:
            single_report, _ = analyze_products([product])
            issues = single_report[0].get("issues", [])
            
            result = AutoOptimizingAgent.optimize_product(product, issues)
            if result.get("success"):
                updated_product = result.get("product")
                
                # Save to simulated cache to persist updates locally
                sim_db = load_simulated_products()
                sim_db[str(pid)] = updated_product
                save_simulated_products(sim_db)
                
                new_report, _ = analyze_products([updated_product])
                results[pid] = {
                    "success": True,
                    "new_score": new_report[0].get("score"),
                    "new_issues": new_report[0].get("issues"),
                    "demo_mode": result.get("demo_mode", False),
                    "new_image_url": new_report[0].get("image_url")
                }
            else:
                results[pid] = {"success": False, "error": result.get("error")}
        except Exception as e:
            results[pid] = {"success": False, "error": str(e)}
            
    return jsonify({"success": True, "results": results})


@app.route("/api/marketing-copy/<product_id>", methods=["GET"])
def marketing_copy_endpoint(product_id):
    products = get_cached_products()
    product = None
    for p in products:
        if str(p.get("id")) == str(product_id):
            product = p
            break
            
    if not product:
        return jsonify({"error": "Product not found"}), 404
        
    copy = MarketingCopyAgent.generate_copy(product)
    return jsonify(copy)


@app.route("/api/competitor-analyze", methods=["POST"])
def competitor_analyze_endpoint():
    data = request.get_json() or {}
    product_id = data.get("product_id")
    competitor_url = data.get("competitor_url")
    
    if not product_id or not competitor_url:
        return jsonify({"error": "Missing product_id or competitor_url"}), 400
        
    products = get_cached_products()
    product = None
    for p in products:
        if str(p.get("id")) == str(product_id):
            product = p
            break
            
    if not product:
        return jsonify({"error": "Product not found"}), 404
        
    analysis = CompetitorAnalysisAgent.analyze(competitor_url, product)
    return jsonify(analysis)


@app.route("/api/generate-mockup", methods=["POST"])
def generate_mockup_endpoint():
    data = request.get_json() or {}
    product_id = data.get("product_id")
    style_preset = data.get("style_preset", "marble")
    
    if not product_id:
        return jsonify({"error": "Missing product_id"}), 400
        
    products = get_cached_products()
    product = None
    for p in products:
        if str(p.get("id")) == str(product_id):
            product = p
            break
            
    if not product:
        return jsonify({"error": "Product not found"}), 404
        
    result = AutoOptimizingAgent.generate_mockup(product, style_preset)
    
    # Store generated mockup back into simulation cache so it renders properly in UI
    if result.get("success") and result.get("mockup_url"):
        sim_db = load_simulated_products()
        if str(product_id) not in sim_db:
            sim_db[str(product_id)] = product.copy()
        sim_db[str(product_id)]["images"] = [{"src": result["mockup_url"]}]
        save_simulated_products(sim_db)
        
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, port=5000)