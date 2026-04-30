import inspect
import json
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from importlib_resources import as_file, files

with as_file(files("loganalyzer")) as path:
    sys.path.append(str(path))
    import loganalyzer.loganalyzer as analyze


htmlTemplate = inspect.cleandoc("""
    <!DOCTYPE html>
    <html lang="zh">
    <head>
        <meta charset="UTF-8">
        <link rel="icon" href="/favicon.ico">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Vite App</title>
        <script type="module" crossorigin src="/assets/index.js"></script>
        <link rel="stylesheet" crossorigin href="/assets/index.css">
    </head>
    <body>
        <pre>{details}</pre>
        <div id="app"></div>
    </body>
    </html>
""")


def checkUrl(url):
    """Check if the incoming URL can be analyzed"""
    return any(
        (
            analyze.matchGist(url),
            analyze.matchHaste(url),
            analyze.matchObs(url),
            analyze.matchPastebin(url),
            analyze.matchDiscord(url),
        )
    )


def genFullHtmlResponse(url):
    """Runs an analysis and returns a full HTML page with the response."""
    return htmlTemplate.format(details=genJsonResponse(url, detailed=True))


def genEmptyHtmlResponse():
    """Generates a full HTML page with no analysis."""
    return htmlTemplate.format(details="{}")


def genJsonResponse(url, detailed):
    """Runs an analysis and returns the results as JSON."""
    msgs = []
    msgs = analyze.doAnalysis(url=url)
    critical = []
    warning = []
    info = []
    for i in msgs:
        entry = i[1]
        if detailed:
            entry = {"title": i[1], "details": i[2]}
        if i[0] == 3:
            critical.append(entry)
        elif i[0] == 2:
            warning.append(entry)
        elif i[0] == 1:
            info.append(entry)
    return {"critical": critical, "warning": warning, "info": info}


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)

        query = {k: v[0] for k, v in parse_qs(urlparse(self.path).query).items()}
        format_ = query.get("format", "").lower()

        self.send_header(
            "Content-Type", "application/json" if format_ == "json" else "text/html"
        )
        self.end_headers()

        body = "{}" if format_ == "json" else genEmptyHtmlResponse()
        url = query.get("url")
        if url and checkUrl(url):
            if format_ == "json":
                body = json.dumps(
                    genJsonResponse(url, query.get("detailed") == "true"),
                    ensure_ascii=False,
                    separators=(",", ":"),
                    check_circular=False,
                )
            else:
                body = genFullHtmlResponse(url)

        self.wfile.write(body.encode("utf-8"))
