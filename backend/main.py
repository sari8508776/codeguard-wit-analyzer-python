from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from backend.analyzer import analyze_code
from backend.visualizer import create_combined_charts

app = FastAPI()


@app.post("/alerts")
async def get_alerts(files: list[UploadFile] = File(...)):
    all_alerts = []
    for file in files:
        content = await file.read()
        code_text = content.decode("utf-8")
        analysis = analyze_code(code_text, file.filename)
        all_alerts.extend(analysis["alerts"])
    return {"alerts": all_alerts}


@app.post("/analyze")
async def analyze_and_visualize(files: list[UploadFile] = File(...)):
    global_categories = {"Length": 0, "Docstring": 0, "Unused": 0, "Hebrew": 0, "Syntax": 0}
    global_lengths = []
    file_issue_counts = {}

    for file in files:
        content = await file.read()
        code_text = content.decode("utf-8")
        analysis = analyze_code(code_text, file.filename)

        global_lengths.extend(analysis["function_lengths"])
        file_issue_counts[file.filename] = len(analysis["alerts"])
        for cat, count in analysis["categories"].items():
            global_categories[cat] += count

    img_buf = create_combined_charts(global_categories, global_lengths, file_issue_counts)
    return StreamingResponse(img_buf, media_type="image/png")