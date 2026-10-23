from flask import Flask, jsonify
import requests

app = Flask(__name__)

# ใส่ API Key ของคุณที่นี่ (103a78befb5e3751608876cf51446712)
API_KEY = "YOUR_API_KEY"
SPORT = "soccer_epl"

@app.route('/api/live-arb', methods=['GET'])
def get_live_arb():
    url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds/?apiKey={API_KEY}&regions=eu&markets=h2h&oddsFormat=decimal"
    
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch odds"}), 500
        
    matches = response.json()
    arb_opportunities = []

    for match in matches:
        home_team = match.get('home_team')
        away_team = match.get('away_team')
        
        bookmakers = {b['key']: b for b in match.get('bookmakers', [])}
        
        if 'pinnacle' in bookmakers and 'onexbet' in bookmakers:
            try:
                pin_market = bookmakers['pinnacle']['markets'][0]['outcomes']
                xbet_market = bookmakers['onexbet']['markets'][0]['outcomes']
                
                odds_pin = pin_market[0]['price']
                odds_xbet = xbet_market[1]['price']
                
                prob_sum = (1 / odds_pin) + (1 / odds_xbet)
                if prob_sum < 1:
                    arb_opportunities.append({
                        "home": home_team,
                        "away": away_team,
                        "odds_pin": odds_pin,
                        "odds_xbet": odds_xbet,
                        "profit_margin": round((1 - prob_sum) * 100, 2)
                    })
            except Exception:
                continue

    return jsonify(arb_opportunities)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
