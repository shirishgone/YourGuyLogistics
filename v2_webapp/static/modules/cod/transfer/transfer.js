(function(){
	'use strict';
	function TransferDepositCntrl($mdDialog,deposits){
		var self = this;
		self.total_cod_amount = 0;
		self.deposits = deposits;
		self.deposits.forEach(function(dp){
			self.total_cod_amount += dp.cod_amount;
		});
		self.cancel = function() {
			$mdDialog.cancel();
		};
		self.answer = function(answer) {
			$mdDialog.hide(answer);
		};
	}

	var codTransferCntrl = function($state,$stateParams,$mdDialog,varifiedDeposits,COD,Notification,Vendor){
		var self = this;
		self.params = $stateParams;
		self.varifiedDeposits = varifiedDeposits.payload.data.all_transactions;
		self.total_pages = varifiedDeposits.payload.data.total_pages;
		self.total_deposits = varifiedDeposits.payload.data.total_bank_deposit_count;
		this.searchVendor = this.params.vendor_name;

		if(this.params.start_date){
			this.params.start_date = new Date(this.params.start_date);
		}
		if(this.params.end_date){
			this.params.end_date = new Date(this.params.end_date);
		}
		/*
			@paginate is a function to paginate to the next and previous page 
		*/
		this.paginate = {
			nextpage : function(){
				self.params.page = self.params.page + 1;
				self.getDgs();
			},
			previouspage : function(){
				self.params.page = self.params.page - 1;
				self.getDgs();
			}
		};
		this.handleSelection =  {
			selectedItemArray : [],
			selectedVendor : undefined,
			toggle : function (item){
				if(self.handleSelection.selectedItemArray.length > 0){
					if(item.vendor_id != self.handleSelection.selectedVendor){
						alert("You cannot select different vendor");
						return;
					}
				}
				else{
					self.handleSelection.selectedVendor = item.vendor_id;
				}
				var idx = self.handleSelection.selectedItemArray.indexOf(item);
        		if (idx > -1) self.handleSelection.selectedItemArray.splice(idx, 1);
        		else self.handleSelection.selectedItemArray.push(item);
			},
			exists : function (item) {
        		return self.handleSelection.selectedItemArray.indexOf(item) > -1;

      		},
			addItem : function(item){
				item.selected = true;
				self.handleSelection.selectedItemArray.push(item);
			},
			removeItem : function (item){
				var index = self.selectedItemArray.indexOf(item);
				if(index > -1) {
					item.selected = false;
					self.handleSelection.selectedItemArray.splice(index,1);
					return true;
				}
				else{
					return false;
				}
			},
			isSelected : function(){
				if(self.handleSelection.selectedItemArray.length > 0){
					return true;
				}
				else {
					return false;
				}
			},
			clearAll : function (){
				self.handleSelection.selectedItemArray = [];
				self.handleSelection.selectedVendor = undefined;
				return self.handleSelection.selectedItemArray;
			},
			slectedItemLength : function (){
				return self.handleSelection.selectedItemArray.length;
			},
			getAlltransactionIds : function(){
				var array = [];
				self.handleSelection.selectedItemArray.forEach(function(tr){
					array.push(tr.delivery_id);
				});
				return array;
			}
		};
		/*
			@transferDeposit function to open transfer deposit popup and send a transfer request to server.
		*/
		self.transferDeposit = function(){
			$mdDialog.show({
				controller         : ('EditDgCntrl',['$mdDialog','deposits',TransferDepositCntrl]),
				controllerAs       : 'transferDeposit',
				templateUrl        : '/static/modules/cod/dialog/transfer-deposit.html',
				parent             : angular.element(document.body),
				clickOutsideToClose: false,
				locals             : {
					       deposits : self.handleSelection.selectedItemArray,
				},
			})
			.then(function(dp) {
				dp.total_cod_transferred = parseInt(dp.total_cod_transferred);
				dp.delivery_ids = self.handleSelection.getAlltransactionIds();
				dp.vendor_id = self.handleSelection.selectedVendor;
				Notification.loaderStart();
				COD.tranferToClient.send(dp,function(response){
					Notification.showSuccess('Transfered Successfully');
					Notification.loaderComplete();
					self.handleSelection.clearAll();
					self.getDeposits();
				},function(err){
					Notification.loaderComplete();
				});
			});
		};		
		/*
			@dgSearchTextChange is a function for Delivery guy search for filter. When ever the filtered dg change, 
			this function is called.

			@selectedVendorChange is a callback function after vendor guy selection in the filter.
		*/
		self.vendorSearchTextChange = function(text){
			var search = {
				search : text
			};
			return Vendor.query(search).$promise.then(function (response){
				return response.payload.data.data;
			});
		};

		self.selectedVendorChange = function(vendor){
			if(vendor){
				self.params.vendor_id = vendor.id;
				self.params.vendor_name = vendor.name;
			}
			else{
				self.params.vendor_id = undefined;
				self.params.vendor_name = undefined;
			}
		};
		/*
			@revertToPageOne is a function to revert back to first page if any kind of filter is applied
		*/ 
		this.revertToPageOne = function(){
			self.params.page = 1;
			self.getDeposits();
		};
		/*
			@resetParams funcion to reset the filter.
		*/
		self.resetParams = function(){
			self.params = {};
			self.getDeposits();
		};
		/*
			@getDeposits rleoads the cod controller according too the filter to get the new filtered data.
		*/
		this.getDeposits = function(){
			if (!self.params.vendor_id) {
				self.params.vendor_name = undefined;
			}
			$state.transitionTo($state.current, self.params, { reload: true, inherit: false, notify: true });
		};
	};

	angular.module('Cod')
	.config(['$stateProvider',function($stateProvider) {
		$stateProvider
		.state('home.cod.transfer',{
			url: "^/cod/transfer?page&start_date&end_date&vendor_id&vendor_name",
			templateUrl: "/static/modules/cod/transfer/transfer.html",
			controllerAs : 'transfer',
    		controller: "codTransferCntrl",
    		resolve : {
    			access: ["Access","constants", function (Access,constants) { 
					var allowed_user = [constants.userRole.ACCOUNTS];
					return Access.hasAnyRole(allowed_user); 
    			}],
    			varifiedDeposits : ['COD','$stateParams',function(COD,$stateParams){
    				$stateParams.start_date = ($stateParams.start_date !== undefined) ? new Date($stateParams.start_date).toISOString() : undefined;
    				$stateParams.end_date = ($stateParams.end_date !== undefined) ? new Date($stateParams.end_date).toISOString() : undefined;
    				$stateParams.page = (!isNaN($stateParams.page))? parseInt($stateParams.page): 1;
    				return COD.getVerifiedDeposits.get($stateParams).$promise;
    			}],
    		}
		});
	}])
	.controller('codTransferCntrl', [
		'$state',
		'$stateParams',
		'$mdDialog',
		'varifiedDeposits',
		'COD',
		'Notification',
		'Vendor',
		codTransferCntrl
	]);
})();