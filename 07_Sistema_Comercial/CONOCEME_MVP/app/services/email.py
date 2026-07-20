import json
import urllib.request


class ResendEmailService:
    endpoint = "https://api.resend.com/emails"

    def __init__(self, api_key, from_email, simulate=False):
        self.api_key = api_key
        self.from_email = from_email
        self.simulate = simulate

    def send(self, *, to, subject, html, idempotency_key):
        if self.simulate:
            return {"id": f"simulated:{idempotency_key}"}
        if not self.api_key or not self.from_email:
            raise RuntimeError("Resend no está configurado")
        payload = json.dumps(
            {"from": self.from_email, "to": [to], "subject": subject, "html": html}
        ).encode("utf-8")
        request = urllib.request.Request(
            self.endpoint,
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Idempotency-Key": idempotency_key,
                "User-Agent": "Serenamente-CONOCEME/1.0",
            },
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
