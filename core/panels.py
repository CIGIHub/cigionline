import base64
import io

from django.urls import reverse
from wagtail.admin.panels import Panel


class QRCodePanel(Panel):
    """
    A read-only Wagtail admin panel that generates and displays a QR code
    pointing to a redirect URL that increments a scan counter before
    forwarding to the page's real public URL.
    """

    class BoundPanel(Panel.BoundPanel):
        template_name = "wagtailadmin/panels/qrcode_panel.html"

        def get_context_data(self, parent_context=None):
            context = super().get_context_data(parent_context)
            context["qr_image_data"] = self._build_qr_data_uri()
            context["page_url"] = self._get_full_url()
            context["scan_count"] = self._get_scan_count()
            return context

        def _get_full_url(self):
            try:
                return self.instance.full_url
            except Exception:
                return None

        def _get_redirect_url(self):
            """Absolute URL of the /qr/<id>/ redirect endpoint encoded in the QR."""
            try:
                if not self.instance.id or not self.instance.live:
                    return None
                path = reverse('qr_redirect', args=[self.instance.id])
                return self.request.build_absolute_uri(path)
            except Exception:
                return None

        def _get_scan_count(self):
            try:
                from .models import QRCodeScan
                return QRCodeScan.objects.get(page_id=self.instance.id).scan_count
            except Exception:
                return 0

        def _build_qr_data_uri(self):
            url = self._get_redirect_url()
            if not url:
                return None
            try:
                import qrcode

                qr = qrcode.QRCode(
                    error_correction=qrcode.constants.ERROR_CORRECT_M,
                    box_size=6,
                    border=4,
                )
                qr.add_data(url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
                return f"data:image/png;base64,{encoded}"
            except ImportError:
                return None
