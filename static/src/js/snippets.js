/** @odoo-module */
import { renderToElement } from "@web/core/utils/render";
import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.get_property_tab = publicWidget.Widget.extend({
    selector : '.properties_section',
    async willStart() {
        const result = await rpc('/get_latest_properties', {});
        if(result){
            this.$target.empty().html(renderToElement('property_management.property_data', {result: result}))
        }
    },
});
