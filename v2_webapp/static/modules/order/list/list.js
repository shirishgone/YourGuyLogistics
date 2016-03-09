(function(){
	'use strict';
	var opsOrderCntrl = function ($state,$mdSidenav,$mdDialog,$mdMedia,$stateParams,DeliveryGuy,Order,Vendor,orders,constants,orderSelection,Pincodes,$q,orderDgAssign){
		/*
			 Variable definations for the route(Url)
		*/
		var self = this;
		this.params = $stateParams;
		this.params.order_status = ($stateParams.order_status)? $stateParams.order_status.split(','): [];
		this.params.pincodes     = ($stateParams.pincodes)    ? $stateParams.pincodes.split(','): [];
		this.params.date         = new Date(this.params.date);
		this.searchedDg          = this.params.dg_username;
		this.searchVendor        = this.params.vendor_id;
		/*
			 scope Orders variable assignments are done from this section for the controller
		*/
		this.orders = orders.payload.data.data;
		this.orderFrom = ( ( ( this.params.page -1 ) * 50 ) + 1 );
		this.orderTo  = (this.orderFrom-1) + orders.payload.data.data.length;
		this.total_pages = orders.payload.data.total_pages;
		this.total_orders = orders.payload.data.total_orders;
		this.pending_orders_count = orders.payload.data.pending_orders_count;
		this.unassigned_orders_count = orders.payload.data.unassigned_orders_count;
		this.pincodes = Pincodes.payload.data;
		/*
			@ status_list: scope order status for eg: 'INTRANSIT' ,'DELIVERED' variable assignments.
			@ time_list: scope order time for time filer variable assignments.
		*/
		this.status_list = constants.status;
		this.time_list = constants.time;
		/*
			@ All method defination for the controller starts from here on.
		*/
		/*
			 @ toggleFilter : main sidenav toggle function, this function toggle the sidebar of the filets of the orders page page.
		*/
		this.toggleFilter = function(){
			$mdSidenav('order-filter').toggle();
		};
		/*
			@pagerange: funxtion for total pages generations for pagination
		*/
		this.pageRange = function (n){
			return new Array(n);
		};
		/*
			@paginate is a function to paginate to the next and previous page of the order list
			@statusSelection is a fucntion to select or unselect the status data in order filter
			@pincodesSelection is a function select unselect multiple pincode in order filter
		*/
		this.paginate = {
			nextpage : function(){
				self.params.page = self.params.page + 1;
				self.getOrders();
			},
			previouspage : function(){
				self.params.page = self.params.page - 1;
				self.getOrders();
			}
		};
		this.statusSelection = {
			toggle : function (item , list){
				var idx = list.indexOf(item.value);
        		if (idx > -1) list.splice(idx, 1);
        		else list.push(item.value);
			},
			exists : function (item, list) {
        		return list.indexOf(item.value) > -1;

      		}
		};
		this.pincodesSelection = {
			toggle : function (item , list){
				var idx = list.indexOf(item.pincode);
        		if (idx > -1) list.splice(idx, 1);
        		else list.push(item.pincode);
			},
			exists : function (item, list) {
        		return list.indexOf(item.pincode) > -1;

      		}
		};
		/*
			@dgSearchTextChange is a function for Delivery guy search for filter. When ever the filtered dg change, 
			this function is called.

			@selectedDgChange is a callback function after delivery guy selection in the filter.
		*/
		this.dgSearchTextChange = function(text){
			var search = {
				search : text
			};
			return DeliveryGuy.dgPageQuery.query(search).$promise.then(function (response){
				return response.payload.data.data;
			});
		};
		this.selectedDgChange = function(dg){
			if(dg){
				self.params.dg_username = dg.phone_number;
			}
			else{
				self.params.dg_username = undefined;
			}
		};
		/*
			@dgSearchTextChange is a function for Delivery guy search for filter. When ever the filtered dg change, 
			this function is called.

			@selectedDgChange is a callback function after delivery guy selection in the filter.
		*/
		this.vendorSearchTextChange = function(text){
			var search = {
				search : text
			};
			return Vendor.query(search).$promise.then(function (response){
				return response.payload.data.data;
			});
		};
		this.selectedVendorChange = function(vendor){
			if(vendor){
				self.params.vendor_id = vendor.id;
			}
			else{
				self.params.vendor_id = undefined;
			}
		};
		/*
			@getOrders rleoads the order controller according too the filter to get the new filtered data.
		*/
		this.handleOrdeSelection = {
			selectActive : orderSelection.isSelected(),
			numberOfSelectedOrder : orderSelection.slectedItemLength(),
			update : function () {
				self.handleOrdeSelection.selectActive = orderSelection.isSelected();
				self.handleOrdeSelection.numberOfSelectedOrder = orderSelection.slectedItemLength();
			},
			toggle : function(item){
				orderSelection.toggle(item);
				self.handleOrdeSelection.update();
			},
			exists : function(item){
				return orderSelection.exists(item);
			},
			clear : function (){
				orderSelection.clearAll();
				self.handleOrdeSelection.update();
			}
		};
		/*
			@assignDg is a function to open dg assignment dialog box and assign delivery guy and pickup guy for the 
			selected orders once user confirms things.
		*/
		self.assignDg = function(){
			orderDgAssign.openDgDialog()
			.then(function(assign_data) {
				assign_data.pickup.delivery_ids = orderSelection.getAllItemsIds();
				assign_data.delivery.delivery_ids = orderSelection.getAllItemsIds();
				self.assignOrders(assign_data);
			}, function() {
				self.status = 'You cancelled the dialog.';
			});
		};
		self.assignDgForSingleOrder = function(order){
			orderDgAssign.openDgDialog()
			.then(function(assign_data) {
				assign_data.pickup.delivery_ids = [order.id];
				assign_data.delivery.delivery_ids = [order.id];
				self.assignOrders(assign_data);
			}, function() {
				self.status = 'You cancelled the dialog.';
			});
		};
		/*
			@assignOrders is a function to call the order assign api from Order service and handle the response.
		*/
		self.assignOrders = function(assign_data){
			var array = [];
			if(assign_data.pickup.dg_id){
				array.push(Order.assignOrders.assign(assign_data.pickup).$promise);
			}
			if(assign_data.delivery.dg_id){
				array.push(Order.assignOrders.assign(assign_data.delivery).$promise);
			}
			$q.all(array).then(function(data){
				orderSelection.clearAll();
				self.getOrders();
			});
		};
		/*
			@getOrders rleoads the order controller according too the filter to get the new filtered data.
		*/
		this.getOrders = function(){
			$state.transitionTo($state.current, self.params, { reload: true, inherit: false, notify: true });
		};
	};

	angular.module('order')
	.controller('opsOrderCntrl', [
		'$state',
		'$mdSidenav',
		'$mdDialog',
		'$mdMedia',
		'$stateParams',
		'DeliveryGuy',
		'Order',
		'Vendor',
		'orders',
		'constants',
		'orderSelection',
		'Pincodes',
		'$q',
		'orderDgAssign',
		opsOrderCntrl
	]);
})();