/** @odoo-module **/
// Part of Odoo. See LICENSE file for full copyright and licensing details.

/**
 * Museum — dual-barcode kiosk extension
 *
 * Patches WelcomePageMembers._onBarcodeScanned so that from the same scanner
 * screen the kiosk can check in both:
 *   • Members  (via the existing partner/grade logic → RegisterPage)
 *   • Event Attendees  (via event.registration.register_attendee → EventRegistrationSummaryDialog)
 *
 * The branching key is `event_checkin` injected by the Python controller
 * (museum/controllers/main.py).
 */

import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";
import { url } from "@web/core/utils/urls";
import { WelcomePageMembers } from "@frontdesk_partnership/welcome_page/welcome_page_members";
import { MuseumEventSummaryDialog } from "./museum_event_summary_dialog";

patch(WelcomePageMembers.prototype, {
    /**
     * Extend onWillStart to also load the 'notify' sound required by
     * EventRegistrationSummaryDialog's playSound callback.
     */
    async onWillStart() {
        await super.onWillStart(...arguments);
        const fileExtension = new Audio().canPlayType("audio/ogg") ? "ogg" : "mp3";
        // Augment the existing sounds map with the event-specific notify sound.
        this.sounds.notify = new Audio(
            url(`/mail/static/src/audio/ting.${fileExtension}`)
        );
        this.sounds.notify.load();
    },

    /**
     * Override _onBarcodeScanned to perform a single RPC and then branch:
     *   - result.event_checkin = true  → open EventRegistrationSummaryDialog
     *   - otherwise                    → original member check-in flow
     *
     * Error handling: UserError from the server (neither member nor event ticket)
     * is caught by the existing error boundary and plays the error sound — no
     * extra handling needed here.
     *
     * @param {string} barcode
     */
    async _onBarcodeScanned(barcode) {
        let result;
        try {
            result = await rpc(
                `/frontdesk/${this.props.stationInfo.id}/${this.props.token}/get_visitor_data`,
                { barcode }
            );
        } catch (error) {
            this.playSound("error");
            throw error;
        }

        if (!result) {
            // Should not happen given the controller always returns or raises,
            // but guard defensively.
            this.playSound("error");
            return barcode;
        }

        if (result.event_checkin) {
            // ── Event ticket barcode ──────────────────────────────────────
            // Play the correct sound immediately, before the dialog mounts.
            //   confirmed_registration / unconfirmed_registration → success
            //   already_registered / need_manual_confirmation     → notify
            //   not_ongoing_event / canceled_registration         → error
            const status = result.status;
            if (["confirmed_registration", "unconfirmed_registration"].includes(status)) {
                this.playSound("success");
            } else if (["already_registered", "need_manual_confirmation"].includes(status)) {
                this.playSound("notify");
            } else {
                this.playSound("error");
            }
            this.dialogService.closeAll();
            this.dialogService.add(MuseumEventSummaryDialog, {
                registration: result,
                playSound: (type) => this.playSound(type),
            });
        } else {
            // ── Member barcode ────────────────────────────────────────────
            // Replicate the original member flow from the base class exactly.
            this.props.setVisitorData(
                result.name,
                result.phone || false,
                result.email || false,
                result.company || false
            );
            this.dialogService.closeAll();
            this.playSound("success");
            this.props.showScreen("RegisterPage");
        }

        return barcode;
    },
});
