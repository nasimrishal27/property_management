/** @odoo-module **/
import { rpc } from "@web/core/network/rpc";
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.generic_form_data = publicWidget.Widget.extend({
   	selector: '#wrap', events: {
       	'click .add_total_property': '_onClickAdd_total_property',
       	'click .remove_line': '_onClickRemove_line',
       	"change #from_date" : "_onDateCalculate",
       	"change #to_date" : "_onDateCalculate",
       	"change .property-selection" : "_onPropertySelection",
       	"change .property_type" : "_onPropertyType",
       	'click #dismiss':'_onCloseClick',
       	'click .record_create':'_onClickSubmit',
   	},

   	_onClickRemove_line: function(ev){
        $(ev.target).parent().parent().remove();
        this._calculateGrandTotal();
    },

    _calculateGrandTotal: function() {
        var grandTotal = 0;
        var currencySymbol = this.$el.find('#grand_total').data('currency-symbol') || '$';
        this.$el.find('.sub_total').each(function() {
            var val = parseFloat($(this).val()) || 0;
            grandTotal += val;
        });
        this.$el.find('#grand_total').text('Grand Total: ' + currencySymbol+  ' ' + grandTotal.toFixed(2));
    },

   	_onClickAdd_total_property: function(ev){
        var rows = this.$el.find('#property_table tbody tr');
    	var new_row = this.$el.find('.add_extra_property').clone(true);
    	var modal = this.el.querySelector('#modal_msg');
        var msg = this.el.querySelector('.modal-title');
        new_row.removeClass('d-none');
     	new_row.removeClass('add_extra_property');
    	new_row.addClass('property_cost_line');
        new_row.insertBefore($('.add_extra_property'));
        new_row.find('#property-selection').val("");
        rows.each(function(index, elem){
               if($(elem).find('#property-selection').val()== null){
                       msg.innerHTML="Fill the previous row";
                       modal.style.display='block';
                       elem.remove()
               }
               else{
                     new_row.insertAfter();
               }
               })
    },

    _onDateCalculate(ev){
        var from_date = new Date(this.$el.find('#from_date').val())
        var to_date = new Date(this.$el.find('#to_date').val())
        var total_days = this.$el.find('#days_count');
        var no_total_days = this.$el.find('.days');
        var $property = $(ev.currentTarget);
        var modal = this.el.querySelector('#modal_msg');
        var msg = this.el.querySelector('.modal-title');
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
        if(msg.textContent == "Choose Date Correctly"){
            to_date.val("")
            from_date.val("")
            modal.style.display='none';
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

    _refreshPropertyRow: function($property) {
        var propertyId = parseInt($property.val());
        var $row = $property.closest('tr');
        var propertyType = $('.property_type').val();
        var $amountInput = $row.find('.rent_lease_amount');
        var $sub_total = $row.find('.sub_total');
        var total_days = parseInt($('.days').val());
        if (!propertyId || !propertyType) {
            console.log("Invalid selection for refresh");
            return;
        }

        rpc('/get/property/amount', {
            property_id: propertyId,
            property_type: propertyType
        }).then((result) => {
            $amountInput.val(result.amount);
            $sub_total.val(result.amount * total_days);
            this._calculateGrandTotal();
        });
    },

    _onPropertySelection: function(ev) {
        var $property = $(ev.currentTarget);
        this._refreshPropertyRow($property);
    },

    _onClickSubmit : async function(ev){
        var modal = this.el.querySelector('#modal_msg');
        var msg = this.el.querySelector('.modal-title');
        var from_date = this.$el.find('#from_date').val()
        var to_date = this.$el.find('#to_date').val()
        var type = this.$el.find('.property_type').val()
        var property_data = [];
        var user_data = [];
        if(from_date.length==0 || to_date.length==0){
            msg.innerHTML="Date not provided";
            modal.style.display='block';
            ev.preventDefault();
            ev.stopPropagation();
        }
        else{
            user_data.push({'from_date':from_date, 'to_date':to_date, 'type':type});
            var hasError = false;
            var rows = this.$el.find('#property_table tbody tr');
            rows.each(function(index, elem){
                if(!elem.classList.contains('d-none')){
                    let row = $(elem)
                    let property = row.find('#property-selection').val();
                    if (property==null || property=='Select a Property'){
                        msg.innerHTML="Completely fill property details"
                        modal.style.display='block';
                        row.remove()
                        hasError = true;
                        ev.preventDefault();
                    }
                    else{
                        property_data.push({'property': property,});
                    }
                }
            })
            if(property_data.length == 0 || hasError){
                msg.innerHTML="Property not selected"
                modal.style.display='block';
                ev.preventDefault();
            }
            else{
                const response = await rpc('/property-shop/submit', {'data' : property_data , 'user_data': user_data});
                if (response) {
                    window.location.href = "/property-shop/success";
                }
            }
        }
    },
});
