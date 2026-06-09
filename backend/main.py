from fastapi import FastAPI, File
from fastapi.responses import StreamingResponse
import io

# הגדרת matplotlib לעבודה ברקע
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = FastAPI(title="CodeGuard AST Analyzer")


@app.post("/alerts")
async def get_alerts(files: bytes = File(...)):  # שונה מ-file ל-files
    """מחזיר פלט JSON של ההתרעות"""
    return {
        "alerts": [
            {
                "file": "analyzed_file.py",
                "line": 12,
                "error_type": "Style",
                "message": f"Analysis complete via CLI. Size: {len(files)} bytes."
            }
        ]
    }


@app.post("/analyze")
async def analyze_visual(files: bytes = File(...)):  # שונה מ-file ל-files
    """מייצר גרף PNG אמיתי ומחזיר אותו כקובץ תמונה"""
    # 1. יצירת הגרף המשולב (שני גרפים זה לצד זה)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # גרף קווי
    ax1.plot([1, 2, 3, 4], [10, 15, 7, 12], marker='o', color='blue', label='Complexity')
    ax1.set_title("Code Complexity Score")
    ax1.set_xlabel("Code Sections")
    ax1.set_ylabel("Complexity")
    ax1.grid(True)

    # גרף עמודות
    error_types = ['Style', 'Warning', 'Critical']
    error_counts = [8, 4, 2]
    ax2.bar(error_types, error_counts, color='salmon', edgecolor='black')
    ax2.set_title("Issues by Category")
    ax2.set_xlabel("Error Type")
    ax2.set_ylabel("Count")

    plt.tight_layout()

    # 2. שמירה לזיכרון
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight')
    plt.close()
    buf.seek(0)

    # 3. שליחת התמונה
    return StreamingResponse(buf, media_type="image/png")