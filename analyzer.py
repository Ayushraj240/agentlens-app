from bs4 import BeautifulSoup

def categorize_issues(issues):
    high = []
    medium = []
    low = []
    
    for issue in issues:
        issue_lower = issue.lower()
        
        # High Priority: policies, product type, shipping, no images
        if ("return" in issue_lower or 
            "refund" in issue_lower or 
            "cancellation" in issue_lower or 
            "shipping" in issue_lower or 
            "product type" in issue_lower or 
            "no product images" in issue_lower):
            high.append(issue)
            
        # Medium Priority: descriptions too short, only 1 image, more images needed, missing tags
        elif ("too short" in issue_lower or 
              "one product image" in issue_lower or 
              "more product images" in issue_lower or
              "tags" in issue_lower):
            medium.append(issue)
            
        # Low Priority: warranty, descriptions details, payment trust
        else:
            low.append(issue)
            
    return {
        "high": high,
        "medium": medium,
        "low": low
    }

def analyze_products(products):
    report = []
    total_score = 0

    for product in products:
        score = 0
        issues = []

        description_html = product.get("body_html", "")
        images = product.get("images", [])
        tags = product.get("tags", "")
        product_type = product.get("product_type", "")
        variants = product.get("variants", [])

        # Clean HTML
        text = BeautifulSoup(description_html, "html.parser").get_text() if description_html else ""
        word_count = len(text.split())
        text_lower = text.lower()

        # =========================
        # 1️⃣ DESCRIPTION DEPTH (20)
        # =========================
        if word_count >= 200:
            score += 20
        elif word_count >= 120:
            score += 15
        elif word_count >= 60:
            score += 10
            issues.append("Description could be more detailed")
        else:
            issues.append("Description too short")

        # =========================
        # 2️⃣ IMAGE COMPLETENESS (20)
        # =========================
        if len(images) >= 4:
            score += 20
        elif len(images) >= 2:
            score += 12
            issues.append("Add more product images")
        elif len(images) == 1:
            score += 5
            issues.append("Only one product image")
        else:
            issues.append("No product images")

        # =========================
        # 3️⃣ POLICY CLARITY (20)
        # =========================
        policy_score = 0

        if "return" in text_lower:
            policy_score += 7
        else:
            issues.append("Return policy not mentioned")

        if "refund" in text_lower:
            policy_score += 7
        else:
            issues.append("Refund info missing")

        if "cancellation" in text_lower:
            policy_score += 6
        else:
            issues.append("Cancellation policy missing")

        score += policy_score

        # =========================
        # 4️⃣ STRUCTURED DATA (20)
        # =========================
        structured_score = 0

        if tags:
            structured_score += 7
        else:
            issues.append("Missing product tags")

        if product_type:
            structured_score += 7
        else:
            issues.append("Product type not defined")

        if len(variants) > 1:
            structured_score += 6

        score += structured_score

        # =========================
        # 5️⃣ TRUST SIGNALS (20)
        # =========================
        trust_score = 0

        if "warranty" in text_lower:
            trust_score += 7
        else:
            issues.append("Warranty not mentioned")

        if "shipping" in text_lower:
            trust_score += 7
        else:
            issues.append("Shipping info missing")

        if "secure payment" in text_lower or "cash on delivery" in text_lower:
            trust_score += 6
        else:
            issues.append("Payment trust signals missing")

        score += trust_score

        # Ensure max 100
        if score > 100:
            score = 100

        total_score += score

        # Get primary image URL
        image_url = None
        if product.get("image") and isinstance(product.get("image"), dict):
            image_url = product.get("image").get("src")
        elif product.get("images") and len(product.get("images")) > 0:
            image_url = product.get("images")[0].get("src")

        report.append({
            "id": product.get("id"),
            "title": product.get("title", "Untitled Product"),
            "score": score,
            "issues": issues,
            "categorized_issues": categorize_issues(issues),
            "image_url": image_url
        })

    avg_score = total_score / len(products) if products else 0

    return report, round(avg_score, 2)