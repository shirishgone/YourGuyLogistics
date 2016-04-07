(function(){
	'use strict';
	var codEdit = function($mdMedia,$mdDialog){
		return {
			openCodDialog : function(){
				return $mdDialog.show({
					controller         : ('EditCodCntrl',['$mdDialog',EditCodCntrl]),
					controllerAs       : 'editCod',
					templateUrl        : '/static/modules/order/dialogs/edit-cod.html?nd=' + Date.now(),
					parent             : angular.element(document.body),
					clickOutsideToClose: false,
					fullscreen         : false,
					openFrom           : '#options',
					closeTo            : '#options',
				});
			}

		};
	};
	/*
		@EditCodCntrl controller function for the edit cod for orders dialog
	*/
	function EditCodCntrl($mdDialog){
		var self = this;
		this.cod_object = {
		};

		this.cancel = function() {
			$mdDialog.cancel();
		};
		this.answer = function(answer){
			$mdDialog.hide(answer);
		};
	}

	angular.module('order')
	.factory('EditCod', [
		'$mdMedia',
		'$mdDialog',
		codEdit
	]);
})();