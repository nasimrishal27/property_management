/** @odoo-module **/
import { rpc } from "@web/core/network/rpc";
import publicWidget from "@web/legacy/js/public/public_widget";
import { renderToElement } from "@web/core/utils/render";
import { useRef, useState } from "@odoo/owl";
console.log("keriii")

publicWidget.registry.generic_form_data = publicWidget.Widget.extend({
   	selector: '#wrap', events: {
       	'click .add_total_property': '_onClickAdd_total_property',
       	'click .remove_line': '_onClickRemove_line',
       	'click .custom_create': '_onClickSubmit',
       	"click #dismiss": "_onCloseClick",
       	"change #from_date" : "_onDateCalculate",
       	"change #to_date" : "_onDateCalculate",
   	},

   	_onClickSubmit: async function(ev){
        	var self = this;
        	var order_lines = [];
        	var rows = $('.total_property_costs > tbody > tr.property_cost_line');
        	_.each(rows, function(row) {
            	let property = $(row).find('input[name="property"]').val();
            	let days = $(row).find('input[name="days"]').val();
            	let rent_lease_amount = $(row).find('input[name="rent_lease_amount"]').val();
            	let sub_total = $(row).find('input[name="sub_total"]').val();
            	console.log(property, days, rent_lease_amount, sub_total)
            	order_lines.push({
                	'property': property,
                	'days': days,
                	'rent_lease_amount': rent_lease_amount,
                	'sub_total': sub_total,
            	});
        	});
        	$('textarea[name="order_line_ids"]').val(JSON.stringify(order_lines));

   	},

   	_onClickRemove_line: function(ev){
   	                console.log('hertcgrev')
                	$(ev.target).parent().parent().remove();
    	},

   	_onClickAdd_total_property: function(ev){
   	            console.log('haaii')
   	            var modal_div = this.el.querySelector('#modal_msg');
                var msg = this.el.querySelector('.modal-title');
                var rows = this.$el.find('#property_table tbody tr');
            	var new_row = this.$el.find('.add_extra_property').clone(true);
            	new_row.removeClass('d-none');
            	new_row.removeClass('add_extra_property');
            	new_row.addClass('property_cost_line');
            	new_row.insertBefore($('.add_extra_property'));
            	rows.each(function(index, elem){
               if($(elem).find('#property').val()== null){
                       msg.innerHTML="Fill the previous row";
                       modal_div.style.display='block';
                       elem.remove()}
               else{
                     new_row.insertBefore(rows.eq(0));
               }
               })
    },

    _onDateCalculate(){
           var modal_div = this.el.querySelector('#modal_msg');
           var msg = this.el.querySelector('.modal-title');
           var from_date = new Date(this.$el.find('#from_date').val())
           var to_date = new Date(this.$el.find('#to_date').val())
           var total_days = this.$el.find('#days_count');
           if (from_date > to_date){
                msg.innerHTML="Choose Date Correctly"
                modal_div.style.display='block';
           }
           else if(from_date && to_date){
                 total_days.text('Total Days : '+ (to_date - from_date) / 86_400_000);
           }},

    _onCloseClick(){
            var modal_div = this.el.querySelector('#modal_msg');
            var msg = this.el.querySelector('.modal-title');
            var from_date = this.$el.find('#from_date')
            var to_date = this.$el.find('#to_date')
            var total_days = this.$el.find('#days_count');
            if(msg.textContent == "Choose Date Correctly"){
                    to_date.val("")
                    from_date.val("")
                    modal_div.style.display='none';
                    total_days.text('Total Days : ');
            }
            else{
                modal_div.style.display='none';
            }
     },
});
