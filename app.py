from flask import Flask, request, render_template_string

app = Flask(__name__)

# -----------------------------
# Risk Calculation Function
# -----------------------------
def calculate_diabetes_risk(age, gender, family, rbs, hba1c, bmi, fbs, ppbs, ogtt, bp, chol_med, pcos):
    score = 0

    # Age
    if age >= 45:
        score += 15
    elif age >= 35:
        score += 10

    # Gender
    if gender == "male":
        score += 5

    # Family History
    if family == "yes":
        score += 15

    # Random Blood Sugar
    if rbs >= 200:
        score += 25
    elif rbs >= 140:
        score += 12

    # HbA1c
    if hba1c >= 6.5:
        score += 25
    elif hba1c >= 5.7:
        score += 12

    # BMI
    if bmi >= 30:
        score += 20
    elif bmi >= 25:
        score += 10

    # FBS
    if fbs >= 126:
        score += 20
    elif fbs >= 100:
        score += 10

    # PPBS
    if ppbs >= 200:
        score += 20
    elif ppbs >= 140:
        score += 10

    # OGTT
    if ogtt >= 200:
        score += 25
    elif ogtt >= 140:
        score += 12

    # Hypertension
    if bp == "yes":
        score += 10

    # Cholesterol medication
    if chol_med == "yes":
        score += 10

    # PCOS (only for females)
    if gender == "female" and pcos == "yes":
        score += 10

    return min(score,100)


# -----------------------------
# HTML UI
# -----------------------------
HTML_PAGE = """

<!DOCTYPE html>
<html>
<head>

<title>Type 2 Diabetes Risk Predictor</title>

<style>

body{
font-family:Arial;
background:linear-gradient(120deg,#e3f2fd,#fce4ec);
display:flex;
justify-content:center;
align-items:center;
min-height:100vh;
margin:0;
}

.container{
background:white;
padding:35px;
border-radius:15px;
width:480px;
box-shadow:0 10px 30px rgba(0,0,0,0.15);
}

h2{
text-align:center;
color:#1565c0;
margin-bottom:20px;
}

label{
font-weight:bold;
margin-top:12px;
display:block;
}

input,select{
width:100%;
padding:10px;
margin-top:6px;
border-radius:7px;
border:1px solid #ccc;
}

button{
width:100%;
margin-top:20px;
padding:12px;
border:none;
border-radius:8px;
background:#1976d2;
color:white;
font-size:16px;
cursor:pointer;
}

button:hover{
background:#0d47a1;
}

.result-card{
margin-top:25px;
padding:20px;
border-radius:10px;
text-align:center;
}

.low{
background:#e8f5e9;
color:#2e7d32;
}

.moderate{
background:#fff8e1;
color:#f57f17;
}

.high{
background:#ffebee;
color:#c62828;
}

.progress{
background:#eee;
height:22px;
border-radius:12px;
margin-top:10px;
overflow:hidden;
}

.progress-bar{
height:100%;
background:linear-gradient(90deg,green,yellow,red);
}

.legend{
display:flex;
justify-content:space-between;
font-size:12px;
margin-top:6px;
}

.tips{
margin-top:15px;
font-size:14px;
text-align:left;
}

.disclaimer{
margin-top:15px;
font-size:12px;
color:#777;
text-align:center;
}

</style>
</head>

<body>

<div class="container">

<h2>Type 2 Diabetes Risk Predictor</h2>

<form method="POST">

<label>Age</label>
<input type="number" name="age" required>

<label>Gender</label>
<select name="gender" id="gender">
<option value="male">Male</option>
<option value="female">Female</option>
</select>

<label>Family History of Diabetes</label>
<select name="family">
<option value="no">No</option>
<option value="yes">Yes</option>
</select>

<label>Random Blood Sugar (mg/dL)</label>
<input type="number" name="rbs" required>

<label>HbA1c (%)</label>
<input type="number" step="0.1" name="hba1c" required>

<label>BMI</label>
<input type="number" step="0.1" name="bmi" required>

<label>Fasting Blood Sugar (mg/dL)</label>
<input type="number" name="fbs" required>

<label>Post Prandial Blood Sugar (mg/dL)</label>
<input type="number" name="ppbs" required>

<label>OGTT (2-Hour Glucose mg/dL)</label>
<input type="number" name="ogtt" required>

<label>Do you have Hypertension (High BP)?</label>
<select name="bp">
<option value="no">No</option>
<option value="yes">Yes</option>
</select>

<label>Are you using Cholesterol Medication?</label>
<select name="chol_med">
<option value="no">No</option>
<option value="yes">Yes</option>
</select>

<div id="pcos_field">

<label>Do you have PCOS?</label>
<select name="pcos">
<option value="no">No</option>
<option value="yes">Yes</option>
</select>

</div>

<button type="submit">Predict Risk</button>

</form>

{% if result %}

<div class="result-card {{risk_class}}">

<h3>{{result}}</h3>

<div class="progress">
<div class="progress-bar" style="width:{{score}}%"></div>
</div>

<div class="legend">
<span style="color:green;">Low</span>
<span style="color:orange;">Moderate</span>
<span style="color:red;">High</span>
</div>

<div class="tips">
<b>Recommendations:</b><br>
{{tips}}
</div>

</div>

{% endif %}

<div class="disclaimer">
Educational tool only. Not a medical diagnosis. Consult healthcare professional.
</div>

</div>

<script>

const gender = document.getElementById("gender");
const pcosField = document.getElementById("pcos_field");

function togglePCOS(){
if(gender.value === "female"){
pcosField.style.display = "block";
}else{
pcosField.style.display = "none";
}
}

gender.addEventListener("change",togglePCOS);
togglePCOS();

</script>

</body>
</html>

"""

# -----------------------------
# Main Route
# -----------------------------
@app.route("/", methods=["GET","POST"])
def index():

    result=None
    risk_class=""
    score=0
    tips=""

    if request.method=="POST":

        age=int(request.form["age"])
        gender=request.form["gender"]
        family=request.form["family"]
        rbs=float(request.form["rbs"])
        hba1c=float(request.form["hba1c"])
        bmi=float(request.form["bmi"])
        fbs=float(request.form["fbs"])
        ppbs=float(request.form["ppbs"])
        ogtt=float(request.form["ogtt"])
        bp=request.form["bp"]
        chol_med=request.form["chol_med"]
        pcos=request.form.get("pcos","no")

        score=calculate_diabetes_risk(age,gender,family,rbs,hba1c,bmi,fbs,ppbs,ogtt,bp,chol_med,pcos)

        if score>=70:
            result=f"High Risk ({score}%)"
            risk_class="high"
            tips="Consult doctor. Confirm with laboratory tests and medical evaluation."

        elif score>=40:
            result=f"Moderate Risk ({score}%)"
            risk_class="moderate"
            tips="Improve diet, exercise regularly and monitor blood glucose."

        else:
            result=f"Low Risk ({score}%)"
            risk_class="low"
            tips="Maintain healthy lifestyle and routine screening."

    return render_template_string(HTML_PAGE,result=result,risk_class=risk_class,score=score,tips=tips)


if __name__=="__main__":
    app.run(debug=True)   