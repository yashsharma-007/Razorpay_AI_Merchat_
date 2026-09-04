import logging
import smtplib
import urllib.request
import json
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
from backend.config import settings

logger = logging.getLogger(__name__)

# In-memory audit log for sent email dispatches
sent_email_alerts: List[Dict[str, Any]] = []

class EmailAlertService:
    @staticmethod
    def _send_real_email(to_email: str, subject: str, body_html: str, body_text: str) -> bool:
        """
        Sends a real email using Resend API (if RESEND_API_KEY set) or Gmail SMTP.
        """
        # 1. Try Resend HTTP API if key provided
        if settings.RESEND_API_KEY:
            try:
                payload = json.dumps({
                    "from": "Merchant Pulse AI <onboarding@resend.dev>",
                    "to": [to_email],
                    "subject": subject,
                    "html": body_html,
                    "text": body_text
                }).encode("utf-8")
                
                req = urllib.request.Request(
                    "https://api.resend.com/emails",
                    data=payload,
                    headers={
                        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                        "Content-Type": "application/json",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MerchantPulse/1.0"
                    },
                    method="POST"
                )
                with urllib.request.urlopen(req) as resp:
                    if resp.status in (200, 201):
                        logger.info(f"📧 [RESEND EMAIL DISPATCH SUCCESS] Delivered to {to_email}")
                        return True
            except Exception as e:
                logger.error(f"Resend email dispatch error: {str(e)}")

        # 2. Try Gmail SMTP if credentials configured
        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            clean_password = settings.SMTP_PASSWORD.replace(" ", "")
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = f"Merchant Pulse AI <{settings.SMTP_USER}>"
                msg["To"] = to_email

                part1 = MIMEText(body_text, "plain", "utf-8")
                part2 = MIMEText(body_html, "html", "utf-8")
                msg.attach(part1)
                msg.attach(part2)

                with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                    server.starttls()
                    server.login(settings.SMTP_USER, clean_password)
                    server.sendmail(settings.SMTP_USER, to_email, msg.as_string())

                logger.info(f"📧 [REAL GMAIL SMTP SUCCESS] Delivered to {to_email}")
                return True
            except Exception as e:
                logger.error(f"Failed Gmail SMTP authentication: {str(e)}")
                return False

        return False

    @staticmethod
    async def send_critical_warning_email(
        merchant_email: str,
        subject: str,
        review_text: str,
        rating: int,
        severity: str,
        customer_name: str,
        ai_summary: str,
        action_recommended: str,
        estimated_revenue_at_risk: str = "₹1,84,800",
        affected_checkouts: str = "42 Sessions",
        mttd: str = "2m 41s",
        failure_vector: str = "UPI Gateway 504 Timeout"
    ) -> Dict[str, Any]:
        """
        Trigger Extreme Warning Email for Critical Incidents and Low Rating (1-2★) Payment Complaints.
        """
        stars = "★" * rating + "☆" * (5 - rating)
        formatted_date = datetime.utcnow().strftime("%B %d, %Y - %H:%M UTC")

        body_text = f"""
[CRITICAL ALERT] MERCHANT PULSE AI TELEMETRY
Subject: {subject}
Merchant Recipient: {merchant_email}
Severity: EXTREME CRITICAL | Status: ACTIVE ESCALATION

KEY INCIDENT METRICS:
- Revenue at Risk: {estimated_revenue_at_risk}
- Impacted Checkouts: {affected_checkouts}
- Detection Speed (MTTD): {mttd}
- Primary Failure Vector: {failure_vector}

CUSTOMER COMPLAINT DETAILS:
- Customer: {customer_name} ({rating}/5 Stars)
- Review: "{review_text}"

AI ROOT CAUSE DIAGNOSIS:
{ai_summary}

RECOMMENDED AUTONOMOUS INTERVENTIONS:
{action_recommended}

Access Incident Command Center: http://localhost:3000/dashboard/incidents
        """

        body_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{subject}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0b0f19; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f3f4f6; -webkit-font-smoothing: antialiased;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #0b0f19; padding: 32px 16px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 640px; background-color: #111827; border: 1px solid #1f2937; border-radius: 12px; overflow: hidden; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.04);">
          
          <!-- Top Header Brand Banner -->
          <tr>
            <td style="background: linear-gradient(135deg, #450a0a 0%, #1e1b4b 100%); padding: 24px 32px; border-bottom: 1px solid #374151;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                <tr>
                  <td>
                    <span style="font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 1.5px; color: #fca5a5; background-color: rgba(220, 38, 38, 0.3); border: 1px solid #ef4444; padding: 4px 10px; border-radius: 4px; display: inline-block;">
                      CRITICAL PAYMENT INCIDENT
                    </span>
                    <h1 style="margin: 14px 0 4px 0; font-size: 22px; font-weight: 700; color: #ffffff; letter-spacing: -0.5px;">
                      {subject}
                    </h1>
                    <p style="margin: 0; font-size: 13px; color: #9ca3af;">
                      Merchant Pulse AI Telemetry &bull; Dispatched {formatted_date}
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Content Body -->
          <tr>
            <td style="padding: 32px;">

              <!-- Key Metrics Grid -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 24px;">
                <tr>
                  <td width="50%" style="padding-right: 8px; padding-bottom: 16px;">
                    <div style="background-color: #1f2937; border: 1px solid #374151; border-radius: 8px; padding: 16px;">
                      <div style="font-size: 11px; font-weight: 600; text-transform: uppercase; color: #9ca3af; letter-spacing: 0.5px;">Est. Revenue at Risk</div>
                      <div style="font-size: 20px; font-weight: 800; color: #f87171; margin-top: 6px;">{estimated_revenue_at_risk}</div>
                    </div>
                  </td>
                  <td width="50%" style="padding-left: 8px; padding-bottom: 16px;">
                    <div style="background-color: #1f2937; border: 1px solid #374151; border-radius: 8px; padding: 16px;">
                      <div style="font-size: 11px; font-weight: 600; text-transform: uppercase; color: #9ca3af; letter-spacing: 0.5px;">Affected Checkouts</div>
                      <div style="font-size: 20px; font-weight: 800; color: #fbbf24; margin-top: 6px;">{affected_checkouts}</div>
                    </div>
                  </td>
                </tr>
                <tr>
                  <td width="50%" style="padding-right: 8px;">
                    <div style="background-color: #1f2937; border: 1px solid #374151; border-radius: 8px; padding: 16px;">
                      <div style="font-size: 11px; font-weight: 600; text-transform: uppercase; color: #9ca3af; letter-spacing: 0.5px;">Detection Speed (MTTD)</div>
                      <div style="font-size: 20px; font-weight: 800; color: #34d399; margin-top: 6px;">{mttd}</div>
                    </div>
                  </td>
                  <td width="50%" style="padding-left: 8px;">
                    <div style="background-color: #1f2937; border: 1px solid #374151; border-radius: 8px; padding: 16px;">
                      <div style="font-size: 11px; font-weight: 600; text-transform: uppercase; color: #9ca3af; letter-spacing: 0.5px;">Failure Vector</div>
                      <div style="font-size: 14px; font-weight: 700; color: #38bdf8; margin-top: 8px; word-break: break-word;">{failure_vector}</div>
                    </div>
                  </td>
                </tr>
              </table>

              <!-- Customer Complaint Callout Card -->
              <div style="background-color: #1e293b; border-left: 4px solid #ef4444; border-top: 1px solid #334155; border-right: 1px solid #334155; border-bottom: 1px solid #334155; border-radius: 8px; padding: 20px; margin-bottom: 24px;">
                <div style="display: table; width: 100%; margin-bottom: 10px;">
                  <div style="display: table-cell; font-size: 14px; font-weight: 700; color: #f3f4f6;">
                    Customer: <span style="color: #ffffff;">{customer_name}</span>
                  </div>
                  <div style="display: table-cell; text-align: right; font-size: 14px; color: #fbbf24; font-weight: bold;">
                    {stars} ({rating}.0 / 5.0)
                  </div>
                </div>
                <p style="margin: 0; font-size: 14px; line-height: 1.6; color: #e2e8f0; font-style: italic;">
                  "{review_text}"
                </p>
              </div>

              <!-- AI Root Cause Diagnosis Box -->
              <div style="background-color: #111827; border: 1px solid #374151; border-radius: 8px; padding: 20px; margin-bottom: 24px;">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 10px;">
                  <tr>
                    <td>
                      <span style="font-size: 11px; font-weight: 700; color: #60a5fa; text-transform: uppercase; letter-spacing: 1px;">
                        AI ROOT CAUSE DIAGNOSIS
                      </span>
                    </td>
                  </tr>
                </table>
                <p style="margin: 0; font-size: 14px; line-height: 1.6; color: #d1d5db;">
                  {ai_summary}
                </p>
              </div>

              <!-- Recommended Interventions -->
              <div style="background-color: #064e3b; border: 1px solid #059669; border-radius: 8px; padding: 20px; margin-bottom: 28px;">
                <div style="font-size: 11px; font-weight: 700; color: #6ee7b7; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">
                  RECOMMENDED AUTONOMOUS INTERVENTIONS
                </div>
                <p style="margin: 0; font-size: 14px; line-height: 1.6; color: #ecfdf5; font-weight: 600;">
                  {action_recommended}
                </p>
              </div>

              <!-- CTA Primary Button -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 8px;">
                <tr>
                  <td align="center">
                    <a href="http://localhost:3000/dashboard/incidents" target="_blank" style="display: inline-block; background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); color: #ffffff; text-decoration: none; font-size: 15px; font-weight: 700; padding: 14px 32px; border-radius: 8px; border: 1px solid #f87171; box-shadow: 0 4px 12px rgba(220, 38, 38, 0.4);">
                      Open Incident Command Center &rarr;
                    </a>
                  </td>
                </tr>
              </table>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color: #0b0f19; border-top: 1px solid #1f2937; padding: 24px 32px; text-align: center;">
              <p style="margin: 0 0 6px 0; font-size: 12px; font-weight: 600; color: #9ca3af;">
                Merchant Pulse AI &bull; Autonomous Payment Health Telemetry
              </p>
              <p style="margin: 0; font-size: 11px; color: #6b7280;">
                Razorpay Hackathon Enterprise Edition &bull; Sent to {merchant_email}
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

        real_sent = EmailAlertService._send_real_email(
            to_email=merchant_email,
            subject=subject,
            body_html=body_html,
            body_text=body_text
        )

        email_payload = {
            "id": f"email_warn_{len(sent_email_alerts) + 1001}",
            "type": "EXTREME_WARNING",
            "merchant_email": merchant_email,
            "subject": subject,
            "rating": rating,
            "severity": severity,
            "customer_name": customer_name,
            "review_text": review_text,
            "ai_summary": ai_summary,
            "action_recommended": action_recommended,
            "sent_at": datetime.utcnow().isoformat(),
            "real_smtp_delivered": real_sent,
            "status": "DELIVERED"
        }
        
        sent_email_alerts.insert(0, email_payload)
        logger.info(f"🚨 [EXTREME WARNING EMAIL PROCESSED] To: {merchant_email} | Subject: {subject} | Real Inbox Delivered: {real_sent}")
        
        return email_payload

    @staticmethod
    async def send_regular_feedback_digest_email(
        merchant_email: str,
        total_reviews: int,
        low_ratings_count: int,
        average_rating: float,
        executive_summary: str,
        top_pain_points: List[str],
        recommended_actions: List[str]
    ) -> Dict[str, Any]:
        """
        Trigger Regular Feedback & Review Digest Email summarizing Play Store sentiment and metrics.
        """
        subject = f"[Merchant Pulse AI] Daily Play Store Review & Feedback Digest ({average_rating:.1f}★ Avg)"
        formatted_date = datetime.utcnow().strftime("%B %d, %Y")

        pain_points_text = "\n".join([f"- {p}" for p in top_pain_points])
        actions_text = "\n".join([f"- {a}" for a in recommended_actions])

        body_text = f"""
MERCHANT PULSE AI - DAILY PLAY STORE & FEEDBACK DIGEST
Date: {formatted_date}
Recipient: {merchant_email}

SUMMARY KPI STATS:
- Total Reviews Scraped & Analyzed: {total_reviews}
- Low Rating Complaints (<4★): {low_ratings_count}
- Average Play Store CSAT Rating: {average_rating:.1f} / 5.0 Stars

EXECUTIVE SUMMARY:
{executive_summary}

TOP RECURRING FRICTION & PAIN POINTS:
{pain_points_text}

RECOMMENDED STRATEGIC MERCHANT ACTIONS:
{actions_text}

Explore Full Customer Feedback Analytics: http://localhost:3000/dashboard/signals
        """

        pain_points_html = "".join([
            f'<li style="margin-bottom: 10px; color: #e2e8f0; font-size: 14px; line-height: 1.5;"><strong style="color: #f59e0b;">&bull;</strong> {p}</li>'
            for p in top_pain_points
        ])
        
        actions_html = "".join([
            f'<li style="margin-bottom: 10px; color: #e2e8f0; font-size: 14px; line-height: 1.5;"><strong style="color: #10b981;">&check;</strong> {a}</li>'
            for a in recommended_actions
        ])

        body_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{subject}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0b0f19; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f3f4f6; -webkit-font-smoothing: antialiased;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #0b0f19; padding: 32px 16px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 640px; background-color: #111827; border: 1px solid #1f2937; border-radius: 12px; overflow: hidden; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.04);">
          
          <!-- Top Header Brand Banner -->
          <tr>
            <td style="background: linear-gradient(135deg, #1e1b4b 0%, #1e3a8a 100%); padding: 24px 32px; border-bottom: 1px solid #374151;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                <tr>
                  <td>
                    <span style="font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 1.5px; color: #a5b4fc; background-color: rgba(99, 102, 241, 0.3); border: 1px solid #6366f1; padding: 4px 10px; border-radius: 4px; display: inline-block;">
                      DAILY REVIEW INTELLIGENCE DIGEST
                    </span>
                    <h1 style="margin: 14px 0 4px 0; font-size: 22px; font-weight: 700; color: #ffffff; letter-spacing: -0.5px;">
                      Play Store Feedback & Sentiment Digest
                    </h1>
                    <p style="margin: 0; font-size: 13px; color: #9ca3af;">
                      Merchant Pulse AI Report &bull; {formatted_date}
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Content Body -->
          <tr>
            <td style="padding: 32px;">

              <!-- KPI Metrics 3 Columns -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 24px;">
                <tr>
                  <td width="33%" style="padding-right: 6px;">
                    <div style="background-color: #1f2937; border: 1px solid #374151; border-radius: 8px; padding: 14px; text-align: center;">
                      <div style="font-size: 10px; font-weight: 700; text-transform: uppercase; color: #9ca3af; letter-spacing: 0.5px;">Total Reviews</div>
                      <div style="font-size: 20px; font-weight: 800; color: #60a5fa; margin-top: 4px;">{total_reviews}</div>
                    </div>
                  </td>
                  <td width="33%" style="padding-left: 3px; padding-right: 3px;">
                    <div style="background-color: #1f2937; border: 1px solid #374151; border-radius: 8px; padding: 14px; text-align: center;">
                      <div style="font-size: 10px; font-weight: 700; text-transform: uppercase; color: #9ca3af; letter-spacing: 0.5px;">Low Ratings (&lt;4&starf;)</div>
                      <div style="font-size: 20px; font-weight: 800; color: #f59e0b; margin-top: 4px;">{low_ratings_count}</div>
                    </div>
                  </td>
                  <td width="33%" style="padding-left: 6px;">
                    <div style="background-color: #1f2937; border: 1px solid #374151; border-radius: 8px; padding: 14px; text-align: center;">
                      <div style="font-size: 10px; font-weight: 700; text-transform: uppercase; color: #9ca3af; letter-spacing: 0.5px;">Avg Rating</div>
                      <div style="font-size: 20px; font-weight: 800; color: #10b981; margin-top: 4px;">{average_rating:.1f} &starf;</div>
                    </div>
                  </td>
                </tr>
              </table>

              <!-- Executive Summary Card -->
              <div style="background-color: #1e293b; border-left: 4px solid #3b82f6; border-top: 1px solid #334155; border-right: 1px solid #334155; border-bottom: 1px solid #334155; border-radius: 8px; padding: 20px; margin-bottom: 24px;">
                <div style="font-size: 11px; font-weight: 700; color: #60a5fa; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">
                  EXECUTIVE SENTIMENT SUMMARY
                </div>
                <p style="margin: 0; font-size: 14px; line-height: 1.6; color: #e2e8f0;">
                  {executive_summary}
                </p>
              </div>

              <!-- Top Pain Points Section -->
              <div style="background-color: #111827; border: 1px solid #374151; border-radius: 8px; padding: 20px; margin-bottom: 24px;">
                <div style="font-size: 11px; font-weight: 700; color: #fbbf24; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;">
                  TOP RECURRING PAIN POINTS
                </div>
                <ul style="margin: 0; padding-left: 16px; list-style-type: none;">
                  {pain_points_html}
                </ul>
              </div>

              <!-- Strategic Merchant Recommendations -->
              <div style="background-color: #111827; border: 1px solid #374151; border-radius: 8px; padding: 20px; margin-bottom: 28px;">
                <div style="font-size: 11px; font-weight: 700; color: #34d399; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;">
                  STRATEGIC MERCHANT ACTIONS
                </div>
                <ul style="margin: 0; padding-left: 16px; list-style-type: none;">
                  {actions_html}
                </ul>
              </div>

              <!-- CTA Primary Button -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 8px;">
                <tr>
                  <td align="center">
                    <a href="http://localhost:3000/dashboard/signals" target="_blank" style="display: inline-block; background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%); color: #ffffff; text-decoration: none; font-size: 15px; font-weight: 700; padding: 14px 32px; border-radius: 8px; border: 1px solid #818cf8; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);">
                      Explore Customer Feedback Analytics &rarr;
                    </a>
                  </td>
                </tr>
              </table>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color: #0b0f19; border-top: 1px solid #1f2937; padding: 24px 32px; text-align: center;">
              <p style="margin: 0 0 6px 0; font-size: 12px; font-weight: 600; color: #9ca3af;">
                Merchant Pulse AI &bull; Autonomous Customer Sentiment & Review Intelligence
              </p>
              <p style="margin: 0; font-size: 11px; color: #6b7280;">
                Razorpay Hackathon Enterprise Edition &bull; Sent to {merchant_email}
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

        real_sent = EmailAlertService._send_real_email(
            to_email=merchant_email,
            subject=subject,
            body_html=body_html,
            body_text=body_text
        )

        email_payload = {
            "id": f"email_digest_{len(sent_email_alerts) + 1001}",
            "type": "REGULAR_DIGEST",
            "merchant_email": merchant_email,
            "subject": subject,
            "total_reviews": total_reviews,
            "low_ratings_count": low_ratings_count,
            "average_rating": average_rating,
            "executive_summary": executive_summary,
            "top_pain_points": top_pain_points,
            "recommended_actions": recommended_actions,
            "sent_at": datetime.utcnow().isoformat(),
            "real_smtp_delivered": real_sent,
            "status": "DELIVERED"
        }
        
        sent_email_alerts.insert(0, email_payload)
        logger.info(f"📊 [REGULAR DIGEST EMAIL PROCESSED] To: {merchant_email} | Subject: {subject} | Real Inbox Delivered: {real_sent}")
        
        return email_payload

    @staticmethod
    def get_sent_email_alerts() -> List[Dict[str, Any]]:
        return sent_email_alerts

