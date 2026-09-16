import { Component, t, useProps } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";
import { EventScanView } from "@event/client_action/event_barcode";
import { EventRegistrationSummaryDialog } from "@event/client_action/event_registration_summary_dialog";

export class MuseumMemberCheckinDialog extends Component {
    static template = "museum.MuseumMemberCheckinDialog";
    static components = { Dialog };

    props = useProps({
        close: t.function(),
        member: t.object(),
    });

    get member() {
        return this.props.member;
    }

    get companyName() {
        return this.member.company || "";
    }

    onClose() {
        this.props.close();
    }
}

patch(EventScanView.prototype, {
    setup() {
        super.setup(...arguments);
        this._scanInProgress = false;
    },

    async onBarcodeScanned(barcode, onNextScanTriggered = () => {}) {
        if (!barcode?.trim()) return;

        if (this._scanInProgress) return;
        this._scanInProgress = true;

        try {
            await this._doMuseumBarcodeScan(barcode, onNextScanTriggered);
        } finally {
            this._scanInProgress = false;
        }
    },

    async _doMuseumBarcodeScan(barcode, onNextScanTriggered) {
        const result = await this.orm.call("event.registration", "register_attendee", [], {
            barcode: barcode,
            event_id: this.eventId,
        });

        if (!result.error || result.error !== "invalid_ticket") {
            this.registrationId = result.id;
            this.closeLastDialog?.();
            this.closeLastDialog = this.dialog.add(EventRegistrationSummaryDialog, {
                playSound: (type) => this.playSound(type),
                doNextScan: onNextScanTriggered,
                registration: result,
            });
            return;
        }

        let museumEnabled = false;
        try {
            const companies = await this.orm.searchRead(
                "res.company",
                [],
                ["x_museum_frontdesk_event_checkin"],
                { limit: 1 }
            );
            museumEnabled = Boolean(companies[0]?.x_museum_frontdesk_event_checkin);
        } catch {}

        if (!museumEnabled) {
            this.playSound("error");
            this.notification.add(_t("Invalid ticket"), { type: "danger" });
            return;
        }

        let station = null;
        try {
            const stations = await this.orm.searchRead(
                "frontdesk.frontdesk",
                [["frontdesk_type", "=", "members"], ["name", "=", "Frontdesk Members"]],
                ["id", "name", "access_token"],
                { limit: 1 }
            );
            station = stations[0];
        } catch {}

        if (!station) {
            this.playSound("error");
            this.notification.add(
                _t("No Frontdesk Members station found. Please configure one in Frontdesk → Stations."),
                { type: "warning" }
            );
            return;
        }

        let memberData = null;
        try {
            memberData = await rpc(
                `/frontdesk/${station.id}/${station.access_token}/get_visitor_data`,
                { barcode }
            );
        } catch (error) {
            const serverMsg = error.data?.message || error.message || "";
            const isNotFound = serverMsg.includes("No partner corresponding to this barcode");
            const displayMsg = isNotFound
                ? _t("Invalid barcode.")
                : serverMsg || _t("Invalid barcode.");
            this.playSound("error");
            this.notification.add(displayMsg, { type: "danger" });
            return;
        }

        try {
            await rpc(
                `/frontdesk/${station.id}/${station.access_token}/prepare_visitor_data`,
                {
                    name: memberData.name,
                    phone: memberData.phone || false,
                    email: memberData.email || false,
                    company: memberData.company || false,
                }
            );
        } catch {}

        this.playSound("notify");
        this.closeLastDialog?.();
        this.closeLastDialog = this.dialog.add(MuseumMemberCheckinDialog, {
            member: memberData,
        });
    },
});
