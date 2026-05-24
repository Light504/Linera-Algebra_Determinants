from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

def get_minor(matrix, row, col):
    """Return the minor matrix obtained by deleting row and col."""
    return [
        [matrix[r][c] for c in range(len(matrix[r])) if c != col]
        for r in range(len(matrix)) if r != row
    ]

def determinant(matrix):
    """Recursively compute the determinant via cofactor (Laplace) expansion along row 0."""
    n = len(matrix)
    if n == 1:
        return matrix[0][0]
    if n == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    det = 0
    for col in range(n):
        sign = (-1) ** col
        minor = get_minor(matrix, 0, col)
        det += sign * matrix[0][col] * determinant(minor)
    return det

def determinant_steps(matrix):
    """Return step-by-step cofactor expansion for an n×n matrix."""
    n = len(matrix)
    steps = []

    if n == 1:
        steps.append({
            "desc": "1×1 matrix — determinant is the single element.",
            "value": matrix[0][0]
        })
        return steps, matrix[0][0]

    if n == 2:
        a, b, c, d = matrix[0][0], matrix[0][1], matrix[1][0], matrix[1][1]
        val = a * d - b * c
        steps.append({
            "desc": f"2×2 formula: ad − bc = ({a})({d}) − ({b})({c}) = {a*d} − {b*c} = {val}",
            "value": val
        })
        return steps, val

    cofactor_vals = []
    for col in range(n):
        sign = (-1) ** col
        minor = get_minor(matrix, 0, col)
        minor_det = determinant(minor)
        cof = sign * matrix[0][col] * minor_det
        cofactor_vals.append(cof)
        minor_str = "; ".join(["[" + ", ".join(str(x) for x in row) + "]" for row in minor])
        steps.append({
            "col": col + 1,
            "element": matrix[0][col],
            "sign": "+" if sign == 1 else "−",
            "sign_val": sign,
            "minor_matrix": minor,
            "minor_det": minor_det,
            "cofactor": cof,
            "desc": f"Column {col+1}: sign={'+' if sign==1 else '-'}, element={matrix[0][col]}, M{1}{col+1}={minor_det}, C={cof}"
        })

    total = sum(cofactor_vals)
    return steps, total

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json()
    try:
        matrix = data.get("matrix", [])
        n = len(matrix)
        if n < 1 or n > 6:
            return jsonify({"error": "Matrix size must be between 1 and 6."}), 400
        for row in matrix:
            if len(row) != n:
                return jsonify({"error": "Matrix must be square."}), 400
        matrix = [[float(x) for x in row] for row in matrix]
        steps, det = determinant_steps(matrix)
        return jsonify({"steps": steps, "determinant": det})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
