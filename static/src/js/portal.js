/** @odoo-module **/
import { rpc } from "@web/core/network/rpc";
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.generic_form_data = publicWidget.Widget.extend({
   	selector: '#wrap',
   	events: {
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
        ev.currentTarget.parentElement.parentElement.remove();
        this._calculateGrandTotal();
    },

    _calculateGrandTotal: function () {
        let grandTotal = 0;
        const grandTotalElement = this.el.querySelector('#grand_total');
        const currencySymbol = grandTotalElement?.dataset.currencySymbol || '$';
        const subTotalElements = this.el.querySelectorAll('.sub_total');
        subTotalElements.forEach((el) => {
            const val = parseFloat(el.value) || 0;
            grandTotal += val;
        });
        if (grandTotalElement) {
            grandTotalElement.textContent = `Grand Total: ${currencySymbol} ${grandTotal.toFixed(2)}`;
        }
    },


   	_onClickAdd_total_property: function (ev) {
        const table = this.el.querySelector('#property_table tbody');
        const rows = table.querySelectorAll('tr');
        const templateRow = this.el.querySelector('.add_extra_property');
        const modal = this.el.querySelector('#modal_msg');
        const msg = modal.querySelector('.modal-title');

        let hasEmptyRow = false;
        rows.forEach((row) => {
            const val = row.querySelector('#property-selection')?.value;
            if (!val) {
                msg.textContent = "Fill the previous row";
                modal.style.display = 'block';
                row.remove();
                hasEmptyRow = true;
            }
        });

        if (!hasEmptyRow) {
            const newRow = templateRow.cloneNode(true);
            newRow.classList.remove('d-none', 'add_extra_property');
            newRow.classList.add('property_cost_line');
            newRow.querySelector('#property-selection').value = '';
            table.appendChild(newRow);
        }
    },

    _onDateCalculate: function (ev) {
        const fromDate = new Date(this.el.querySelector('#from_date').value);
        const toDate = new Date(this.el.querySelector('#to_date').value);
        const totalDaysText = this.el.querySelector('#days_count');
        const totalDaysInput = this.el.querySelector('.days');
        const modal = this.el.querySelector('#modal_msg');
        const msg = modal.querySelector('.modal-title');
        if (fromDate > toDate) {
            msg.textContent = "Choose Date Correctly";
            modal.style.display = 'block';
        } else if (fromDate && toDate) {
            const days = (toDate - fromDate) / 86400000;
            totalDaysText.textContent = 'Total Days : ' + days;
            totalDaysInput.value = days;
        }
        this._onPropertyType(ev.currentTarget);
    },

    _onCloseClick: function () {
        const modal = this.el.querySelector('#modal_msg');
        const msg = modal.querySelector('.modal-title');
        const fromDateInput = this.el.querySelector('#from_date');
        const toDateInput = this.el.querySelector('#to_date');
        const totalDaysText = this.el.querySelector('#days_count');

        if (msg.textContent === "Choose Date Correctly") {
            fromDateInput.value = '';
            toDateInput.value = '';
            totalDaysText.textContent = 'Total Days : ';
        }
        modal.style.display = 'none';
    },

    _onPropertyType: function () {
        const selections = this.el.querySelectorAll('.property-selection');
        selections.forEach((el) => {
            this._refreshPropertyRow(el);
        });
    },

    _refreshPropertyRow: function (propertyElement) {
        const propertyId = parseInt(propertyElement.value);
        const row = propertyElement.closest('tr');
        const propertyType = this.el.querySelector('.property_type').value;
        const amountInput = row.querySelector('.rent_lease_amount');
        const subTotalInput = row.querySelector('.sub_total');
        const totalDays = parseInt(this.el.querySelector('.days').value);

        if (!propertyId || !propertyType) {
            console.log("Invalid selection for refresh");
            return;
        }

        rpc('/get/property/amount', {
            property_id: propertyId,
            property_type: propertyType
        }).then((result) => {
            amountInput.value = result.amount;
            subTotalInput.value = (result.amount * totalDays).toFixed(2);
            this._calculateGrandTotal();
        });
    },

    _onPropertySelection: function (ev) {
        this._refreshPropertyRow(ev.currentTarget);
    },

    _onClickSubmit: async function (ev) {
        const modal = this.el.querySelector('#modal_msg');
        const msg = modal.querySelector('.modal-title');
        const fromDate = this.el.querySelector('#from_date').value;
        const toDate = this.el.querySelector('#to_date').value;
        const type = this.el.querySelector('.property_type').value;

        const propertyData = [];
        const userData = [];

        if (!fromDate || !toDate) {
            msg.textContent = "Date not provided";
            modal.style.display = 'block';
            ev.preventDefault();
            ev.stopPropagation();
            return;
        }

        userData.push({ from_date: fromDate, to_date: toDate, type });

        let hasError = false;
        const rows = this.el.querySelectorAll('#property_table tbody tr');
        rows.forEach((row) => {
            if (!row.classList.contains('d-none')) {
                const propVal = row.querySelector('#property-selection')?.value;
                if (!propVal || propVal === 'Select a Property') {
                    msg.textContent = "Completely fill property details";
                    modal.style.display = 'block';
                    row.remove();
                    hasError = true;
                } else {
                    propertyData.push({ property: propVal });
                }
            }
        });

        if (propertyData.length === 0 || hasError) {
            msg.textContent = "Property not selected";
            modal.style.display = 'block';
            ev.preventDefault();
        } else {
            const response = await rpc('/property-shop/submit', {
                data: propertyData,
                user_data: userData,
            });
            if (response) {
                window.location.href = "/property-shop/success";
            }
        }
    },

});
