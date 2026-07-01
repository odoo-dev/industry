import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";

// In the Cost Nature Analysis list view, 
// Computes the margin % from the summed costs & prices instead of summing margin percentages
patch(ListRenderer.prototype, { formatGroupAggregate(group, column) {
    // Writes the correct margin % in the grouped list items 
        if (group.model.config.resModel == "x_cost_nature_analysis_report" && ["x_quantity", "x_margin_percent"].includes(column.name)) {
            return { value: (column.name == "x_margin_percent" && group.aggregates["x_total_price"]) ? Math.round(100 * (group.aggregates["x_margin"]) / group.aggregates["x_total_price"]).toString() + " %" : "" };}
        return super.formatGroupAggregate(group, column);},
    // Writes the correct margin % in the aggregate line below the list
    computeAggregates() { const aggregates = super.computeAggregates();
        if (aggregates && aggregates["x_margin_percent"] && aggregates["x_total_price"] && aggregates["x_margin"]) {
            aggregates["x_margin_percent"].rawValue = aggregates["x_total_price"].rawValue ? 100 * (aggregates["x_margin"].rawValue) / aggregates["x_total_price"].rawValue : 0;
            aggregates["x_margin_percent"].value = Math.round(aggregates["x_margin_percent"].rawValue).toString() + " %";}
        return aggregates;}})
