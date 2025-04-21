/** @odoo-module **/
import { rpc } from "@web/core/network/rpc";
import publicWidget from "@web/legacy/js/public/public_widget";
import { renderToElement } from "@web/core/utils/render";
import { useRef, useState } from "@odoo/owl";

publicWidget.registry.generic_form_data = publicWidget.Widget.extend({
   	selector: '#wrap', events: {
       	'click .add_total_property': '_onClickAdd_total_property',
       	'click .remove_line': '_onClickRemove_line',
       	"click #dismiss": "_onCloseClick",
       	"change #from_date" : "_onDateCalculate",
       	"change #to_date" : "_onDateCalculate",
       	"change .property-selection" : "_onPropertySelection",
       	"change .property-type" : "_onPropertyType",
   	},

   	_onClickRemove_line: function(ev){
                	$(ev.target).parent().parent().remove();
    	},

   	_onClickAdd_total_property: function(ev){
   	            var modal = this.el.querySelector('#modal_msg');
                var msg = this.el.querySelector('.modal-title');
                var rows = this.$el.find('#property_table tbody tr');
            	var new_row = this.$el.find('.add_extra_property').clone(true);
            	new_row.removeClass('d-none');
            	new_row.removeClass('add_extra_property');
            	new_row.addClass('property_cost_line');
            	new_row.insertBefore($('.add_extra_property'));
            	new_row.find('#property-selection').val("")
            	rows.each(function(index, elem){
            	console.log($(elem).find('#property-selection').val())
               if($(elem).find('#property-selection').val()== null){
                       msg.innerHTML="Fill the previous row";
                       modal.style.display='block';
                       elem.remove()}
               else{
                     new_row.insertAfter();
               }
               })
    },

    _onDateCalculate(ev){
           var modal = this.el.querySelector('#modal_msg');
           var msg = this.el.querySelector('.modal-title');
           var from_date = new Date(this.$el.find('#from_date').val())
           var to_date = new Date(this.$el.find('#to_date').val())
           var total_days = this.$el.find('#days_count');
           var no_total_days = this.$el.find('.days');
           var $property = $(ev.currentTarget);
           if (from_date > to_date){
                msg.innerHTML="Choose Date Correctly"
                modal.style.display='block';
           }
           else if(from_date && to_date){
                 total_days.text('Total Days : '+ (to_date - from_date) / 86_400_000);
                 no_total_days.val((to_date - from_date) / 86_400_000)
           }
           this._onPropertyType($property)
    },

    _onCloseClick(){
            var modal = this.el.querySelector('#modal_msg');
            var msg = this.el.querySelector('.modal-title');
            var from_date = this.$el.find('#from_date')
            var to_date = this.$el.find('#to_date')
            var total_days = this.$el.find('#days_count');
            if(msg.textContent == "Choose Date Correctly"){
                    to_date.val("")
                    from_date.val("")
                    modal.style.display='none';
                    total_days.text('Total Days : ');
            }
            else{
                modal.style.display='none';
            }
    },

    _onPropertyType: function(ev) {
        var self = this;
        this.$el.find('.property-selection').each(function() {
            self._refreshPropertyRow($(this));
        });
    },


//    _onPropertySelection(ev){
//        var $property = $(ev.currentTarget);
//        var propertyId = parseInt($property.val());
//        var $row = $property.closest('tr');
//        var propertyType = $('.property-type').val();
//        var $amountInput = $row.find('.rent_lease_amount');
//        var $sub_total = $row.find('.sub_total');
//        var total_days = $('.days').val();
//        console.log(propertyId);
//        console.log(propertyType);
//        console.log("------------");
//        if (!propertyId || !propertyType){
//            console.log("Invalid selection");
//            return;
//        }
//
//        rpc('/get/property/amount', {
//            property_id: propertyId,
//            property_type: propertyType
//        }).then(function (result) {
//            console.log("Amount:", result.amount);
//            $amountInput.val(result.amount);
//            $sub_total.val(result.amount * total_days);
//        });
//    },

    _refreshPropertyRow: function($property) {
        var propertyId = parseInt($property.val());
        var $row = $property.closest('tr');
        var propertyType = $('.property-type').val();
        var $amountInput = $row.find('.rent_lease_amount');
        var $sub_total = $row.find('.sub_total');
        var total_days = parseInt($('.days').val());

        if (!propertyId || !propertyType || !total_days) {
            console.log("Invalid selection for refresh");
            return;
        }

        rpc('/get/property/amount', {
            property_id: propertyId,
            property_type: propertyType
        }).then(function (result) {
            $amountInput.val(result.amount);
            $sub_total.val(result.amount * total_days);
        });
    },

    _onPropertySelection: function(ev) {
        var $property = $(ev.currentTarget);
        this._refreshPropertyRow($property);
    },

});
