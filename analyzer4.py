import json

def analyze_seo_data(seo_data):
    insights = {}

    insights['headers'] = []
    for header_type, header_list in seo_data['headers'].items():
        for header in header_list:
            insights['headers'].append(f"{header_type}: {header}")

    insights['alt_attributes'] = [f"Image with missing alt attribute: {src}" for src, alt in zip(seo_data['images_src'], seo_data['alt_attributes']) if not alt]

    insights['links'] = [f"Link: {link}" for link in seo_data['links']]

    insights['readability_score'] = [f"Readability score: {seo_data['readability_score']}"]

    insights['number_of_images'] = [f"Number of images: {seo_data['number_of_images']}"]

    insights['number_of_links'] = [f"Number of links: {seo_data['number_of_links']}"]

    insights['word_count'] = []
    word_count = seo_data.get('word_count', 0)
    if word_count < 300:
        insights['word_count'].append("Consider increasing the word count on the page to provide more valuable content.")
    elif word_count > 2500:
        insights['word_count'].append("The word count is quite high. Ensure the content is focused and relevant to the target audience.")

    insights['keyword_density'] = []
    keyword_density = seo_data.get('keyword_density', {})
    sorted_keywords = sorted(keyword_density.items(), key=lambda x: x[1], reverse=True)
    filtered_keywords = [(keyword, density) for keyword, density in sorted_keywords if 0.01 <= density <= 0.05]
    for keyword, density in filtered_keywords[:10]:  # Limit to top 10 keywords
        insights['keyword_density'].append(f"The keyword '{keyword}' has a density of {density * 100:.2f}%. Consider optimizing its usage for better results.")

    insights['readability'] = []
    readability_score = seo_data.get('readability_score', 0)
    if readability_score < 60:
        insights['readability'].append("The readability score is low. Consider simplifying the content to make it more accessible to a broader audience.")
    elif readability_score > 80:
        insights['readability'].append("The readability score is high. This is great for general audiences, but make sure the content is still detailed and informative enough for your target audience.")

    insights['sitemap'] = []
    xml_sitemap_exists = seo_data.get('xml_sitemap_exists', False)
    if not xml_sitemap_exists:
        insights['sitemap'].append("No XML sitemap was found. Create and submit an XML sitemap to improve the site's crawlability.")

    insights['ssl_certificate'] = []
    ssl_certificate_valid = seo_data.get('ssl_certificate_valid', False)
    if not ssl_certificate_valid:
        insights['ssl_certificate'].append("The SSL certificate is invalid or missing. Obtain a valid SSL certificate to ensure the website's security and improve search engine rankings.")

    return insights


def create_html_report(insights):
    categories = {
        'headers': 'Headers',
        'alt_attributes': 'Alt Attributes',
        'links': 'Links',
        'readability_score': 'Readability Score',
        'number_of_images': 'Number of Images',
        'number_of_links': 'Number of Links',
        'word_count': 'Word Count',
        'keyword_density': 'Keyword Density',
        'readability': 'Readability',
        'sitemap': 'Sitemap',
        'ssl_certificate': 'SSL Certificate',
    }

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>SEO Insights Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
        }}
        h1, h2 {{
            margin-bottom: 20px;
        }}
        ol {{
            padding-left: 20px;
        }}
        li {{
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <h1>Insights and Action Plan:</h1>
"""

    for category, title in categories.items():
        category_insights = insights.get(category, [])
        if category_insights:
            html += f"<h2>{title}:</h2><ol>"
            for insight in category_insights:
                html += f"<li>{insight}</li>"
            html += "</ol>"

    html += """
</body>
</html>
"""

    return html


def main():
    with open('seo_data.json', 'r') as infile:
        seo_data = json.load(infile)

    insights = analyze_seo_data(seo_data)
    html_report = create_html_report(insights)

    with open('seo_insights_report.html', 'w') as outfile:
        outfile.write(html_report)

    print("The SEO insights report has been saved to 'seo_insights_report.html'.")

if __name__ == "__main__":
    main()
