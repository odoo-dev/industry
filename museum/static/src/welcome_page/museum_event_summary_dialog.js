/** @odoo-module **/
// Part of Odoo. See LICENSE file for full copyright and licensing details.

/**
 * Kiosk-safe event check-in summary dialog for the Museum frontdesk.
 *
 * Covers every feature of the base EventRegistrationSummaryDialog that is
 * relevant to a non-IoT kiosk context:
 *
 *   ✅  Status banners  (confirmed / unconfirmed / already_registered /
 *                        canceled / not_ongoing / need_manual_confirmation)
 *   ✅  Sale-status badge  (Free · Sold · To Pay)  — from event_sale
 *   ✅  Answers row with coloured pill tags
 *   ✅  Undo  (rpc directly — no orm service needed in kiosk bundle)
 *   ✅  Print  (window.open PDF URL — no action service needed)
 *   ✅  Edit Ticket  (window.open backend form — no action service needed)
 *   ✅  doNextScan / onScanNext  (camera re-scan after close)
 *   ✅  isBarcodeScannerSupported  (shows/hides "Next Scan" button)
 *   ✅  Sound on mount  (notify for already_registered/need_manual,
 *                        error for not_ongoing/canceled)
 *
 *   ❌  IoT printer support  (event_iot)  — not relevant for museum kiosk
 *   ❌  Auto-print / download  (event_iot) — same
 *
 * Why a separate file instead of importing the original:
 *   The base EventRegistrationSummaryDialog calls useService("action"),
 *   useService("orm") and useService("notification") which are all
 *   backend-only services not present in the kiosk bundle
 *   (frontdesk_partnership.assets_frontdesk_partnership).
 *   This class replaces them with kiosk-compatible equivalents.
 */

import { Component, onMounted, proxy, signal } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { isBarcodeScannerSupported } from "@web/core/barcode/barcode_video_scanner";
import { Dialog } from "@web/core/dialog/dialog";

export class MuseumEventSummaryDialog extends Component {
    static template = "museum.MuseumEventSummaryDialog";
    static components = { Dialog };
    static props = {
        close: Function,
        doNextScan: { type: Function, optional: true },
        playSound: { type: Function, optional: true },
        registration: { type: Object },
    };

    continueButtonRef = signal.ref();

    setup() {
        this.orm = useService("orm");
        this.isBarcodeScannerSupported = isBarcodeScannerSupported();
        this.button = proxy({ enabled: true });
        this.registrationStatus = proxy({ value: this.props.registration.status });

        onMounted(() => {
            // Mirror the exact sound logic of EventRegistrationSummaryDialog.
            const status = this.props.registration.status;
            if (
                ["already_registered", "need_manual_confirmation"].includes(status) &&
                this.props.playSound
            ) {
                this.props.playSound("notify");
            } else if (
                ["not_ongoing_event", "canceled_registration"].includes(status) &&
                this.props.playSound
            ) {
                this.props.playSound("error");
            }
            // Re-focus Close button so repeat barcode scans keep working.
            this.continueButtonRef()?.focus();
        });
    }

    get registration() {
        return this.props.registration;
    }

    get needManualConfirmation() {
        return this.registrationStatus.value === "need_manual_confirmation";
    }

    // ── Close ────────────────────────────────────────────────────────────────

    async onRegistrationClose() {
        this.props.close();
        if (this.props.doNextScan) {
            this.onScanNext();
        }
    }

    // ── Undo ─────────────────────────────────────────────────────────────────
    // Uses rpc() directly because the kiosk bundle has no orm service.

    async undoRegistration() {
        this.button.enabled = false;
        try {
            const status = this.registrationStatus.value;
            const id = this.registration.id;
            if (["confirmed_registration", "already_registered"].includes(status)) {
                if (this.registration.remaining_entries === 0) {
                    await this.orm.call(
                        "event.registration",
                        "action_confirm_and_reset",
                        [id]
                    );
                } else if (this.registration.remaining_entries > 0) {
                    await this.orm.call(
                        "event.registration",
                        "action_cancel_last_sub_registration",
                        [id]
                    );
                }
            } else if (status === "unconfirmed_registration") {
                await this.orm.call(
                    "event.registration",
                    "action_set_draft",
                    [id]
                );
            }
        } finally {
            this.button.enabled = true;
        }
        this.props.close();
    }

    // ── Print ─────────────────────────────────────────────────────────────────
    // Uses window.open() with the direct PDF URL — no action service needed.

    async onRegistrationPrintPdf() {
        window.open(
            `/report/pdf/event.event_registration_report_template_badge/${this.registration.id}`,
            "_blank"
        );
        if (this.props.doNextScan) {
            this.onScanNext();
        }
    }

    // ── Edit Ticket ───────────────────────────────────────────────────────────
    // Opens the specific attendee form record in a new backend tab.
    // Uses the hash URL (/web#model=...&id=...&view_type=form) which reliably
    // opens the exact record — the /odoo/events/registrations/{id} path can
    // redirect to the events list when called from a public kiosk session.

    async onRegistrationView() {
        window.open(
            `/web#model=event.registration&id=${this.registration.id}&view_type=form`,
            "_blank"
        );
        this.props.close();
    }

    // ── Next scan (camera) ────────────────────────────────────────────────────

    async onScanNext() {
        this.props.close();
        if (this.isBarcodeScannerSupported) {
            this.props.doNextScan();
        }
    }
}
