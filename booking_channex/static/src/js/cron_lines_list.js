import { ListController } from "@web/views/list/list_controller";
import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { useService } from "@web/core/utils/hooks";

export class CronLinesListController extends ListController {
    setup() {
        super.setup();
        this.actionService = useService("action");
        this.notification = useService("notification");
    }
    async onClickSend() {
        await this.actionService.doAction("booking_channex.cron_action_send_data_to_channex");
        this.notification.add("Data sent to Channex.", {type: "success",});
    }
}

export const cronLinesList = {
    ...listView,
    Controller: CronLinesListController,
    buttonTemplate: "booking_channex.CronLinesListView.Buttons",
};

registry.category("views").add("cron_lines_list", cronLinesList);
