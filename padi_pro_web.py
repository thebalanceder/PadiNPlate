"""
Padi AI Pro - Flask Web Application
=================================
Enhanced system with ranked solutions and purchase links.
"""

import os
from flask import Flask, render_template, request, jsonify
from padi_ai_pro import PadiAIPro, SolutionRankingEngine, ProductDatabase

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "padi-ai-pro-secret")

# Initialize engines
ai_pro = PadiAIPro()
ranking_engine = SolutionRankingEngine()
product_db = ProductDatabase()


@app.route("/")
def index():
    return render_template("pro.html")


@app.route("/api/diagnose", methods=["POST"])
def diagnose():
    """Diagnose disease from symptoms."""
    data = request.get_json()

    symptoms = data.get("symptoms", [])
    budget = data.get("budget", "medium")
    urgency = data.get("urgency", "medium")
    preference = data.get("preference", "balanced")
    farm_size = float(data.get("farm_size", 1.0))

    result = ai_pro.analyze_disease(
        symptoms=symptoms,
        budget=budget,
        urgency=urgency,
        preference=preference,
        farm_size_ha=farm_size,
    )

    return jsonify(result)


@app.route("/api/products", methods=["GET"])
def get_products():
    """Get all available products."""
    purpose = request.args.get("purpose", "all")

    if purpose == "all":
        products = product_db.products
    else:
        products = product_db.get_products(purpose)

    return jsonify(
        {
            "products": [
                {
                    "id": pid,
                    "name": p["name"],
                    "brand": p["brand"],
                    "price_rm": p["price_rm"],
                    "unit": p["unit"],
                    "effectiveness": p["effectiveness"],
                    "sources": p.get("sources", []),
                }
                for pid, p in (
                    products.items()
                    if purpose == "all"
                    else [(p.get("product_id", ""), p) for p in products]
                )
            ]
        }
    )


@app.route("/api/rank-solutions", methods=["POST"])
def rank_solutions():
    """Get ranked solutions without full diagnosis."""
    data = request.get_json()

    disease = data.get("disease", "rice_blast")
    severity = data.get("severity", "moderate")
    budget = data.get("budget", "medium")
    urgency = data.get("urgency", "medium")
    preference = data.get("preference", "balanced")

    solutions = ranking_engine.rank_solutions(
        disease=disease,
        severity=severity,
        budget=budget,
        urgency=urgency,
        preference=preference,
    )

    return jsonify(
        {
            "solutions": [
                {
                    "rank": s.rank.value,
                    "name": s.solution_name,
                    "type": s.solution_type,
                    "effectiveness": s.effectiveness,
                    "speed": s.speed,
                    "cost": s.cost,
                    "overall_score": s.overall_score,
                    "time_to_effect_days": s.time_to_effect_days,
                    "safety_level": s.safety_level,
                    "environmental_impact": s.environmental_impact,
                    "products": [
                        {
                            "name": p.name,
                            "price_rm": p.price_rm,
                            "total_cost_rm": p.total_cost_rm,
                            "source": p.purchase_source,
                            "url": p.purchase_url,
                            "delivery_days": p.delivery_days,
                            "effectiveness_score": p.effectiveness_score,
                        }
                        for p in s.products
                    ],
                    "total_cost_rm": s.total_estimated_cost_rm,
                    "pros": s.pros,
                    "cons": s.cons,
                    "recommendations": s.recommendations,
                }
                for s in solutions
            ]
        }
    )


def main():
    print("=" * 60)
    print("PADI AI PRO - ENHANCED SYSTEM")
    print("=" * 60)
    print()
    print("Features:")
    print("  - Disease diagnosis from symptoms")
    print("  - Ranked solutions (S/A/B/C ratings)")
    print("  - Product recommendations with purchase links")
    print("  - Cost analysis (money/quality/time)")
    print()
    print("Starting web server...")
    print("Open http://localhost:5001 in your browser")
    print("=" * 60)

    app.run(host="0.0.0.0", port=5001, debug=True)


if __name__ == "__main__":
    main()
