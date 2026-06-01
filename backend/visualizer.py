import matplotlib.pyplot as plt
import io


def create_combined_charts(all_categories: dict, all_lengths: list, file_issue_counts: dict) -> io.BytesIO:
    fig, axs = plt.subplots(1, 3, figsize=(18, 5))

    # 1. Pie Chart
    filtered_categories = {k: v for k, v in all_categories.items() if v > 0}
    if not filtered_categories:
        filtered_categories = {"Perfect Code": 1}
    axs[0].pie(filtered_categories.values(), labels=filtered_categories.keys(), autopct='%1.1f%%', startangle=90)
    axs[0].set_title("Issues by Type (Pie Chart)")

    # 2. Histogram
    if all_lengths:
        axs[1].hist(all_lengths, bins=range(1, max(all_lengths) + 5, 2), color='skyblue', edgecolor='black')
        axs[1].set_xlabel("Lines of Code")
        axs[1].set_ylabel("Count of Functions")
    else:
        axs[1].text(0.5, 0.5, 'No functions found', ha='center', va='center')
    axs[1].set_title("Function Lengths (Histogram)")

    # 3. Bar Chart
    if file_issue_counts:
        axs[2].bar(file_issue_counts.keys(), file_issue_counts.values(), color='salmon', edgecolor='black')
        axs[2].set_ylabel("Number of Issues")
        axs[2].set_xticklabels(file_issue_counts.keys(), rotation=45, ha='right')
    else:
        axs[2].text(0.5, 0.5, 'No issues found', ha='center', va='center')
    axs[2].set_title("Issues per File (Bar Chart)")

    plt.tight_layout()

    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    plt.close(fig)

    return img_buf