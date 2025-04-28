/** @odoo-module **/
import { renderToElement } from "@web/core/utils/render";
import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

function chunkArray(array, size) {
    const chunks = [];
    for (let i = 0; i < array.length; i += size) {
        chunks.push(array.slice(i, i + size));
    }
    return chunks;
}

publicWidget.registry.get_property_tab = publicWidget.Widget.extend({
    selector : '.properties_section',
    async willStart() {
        const result = await rpc('/get_latest_properties', {});
        if(result && result.properties){
            const chunks = chunkArray(result.properties, 4);
            chunks[0].is_active = true
            this.$target.empty().html(renderToElement('property_management.property_data', {
                property_chunks: chunks,
                currency_symbol: result.currency_symbol,
            }));
        }
    },
});
