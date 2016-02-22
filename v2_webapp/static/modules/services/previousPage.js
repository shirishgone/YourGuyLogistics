(function(){
	'use strict';
	/*
		A service to handle and move to the previous state with all the url parameters,
		this fucntion uses the rootscope previousState object and redirects from the current page 
		to the previous page, and if the page is reloaded or the previous state is empty it returns 
		a boolean data to do validation check and handle the edge case.
	*/
	var PreviousState = function($rootScope,$state){
		return {
			isAvailable : function(){
				if(!$rootScope.previousState.state || $rootScope.previousState.state === ''){
					return false;
				}
				else{
					return true;
				}
			},
			redirectToPrevious : function(){
				$state.go($rootScope.previousState.state,$rootScope.previousState.params);
				return;
			}
		};
	};

	angular.module('ygVendorApp')
	.factory('PreviousState', [
		'$rootScope',
		'$state',
		PreviousState
	]);

})();