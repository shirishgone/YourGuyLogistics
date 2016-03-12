(function(){
	'use strict';
	var Notification = function($rootScope,$state,$document){
		return {
			loaderStart : function(){
				angular.element($document[0].getElementsByClassName('request-loader')).removeClass('request-loader-hidden');
			},
			loaderComplete : function(){
				angular.element($document[0].getElementsByClassName('request-loader')).addClass('request-loader-hidden');
			},
			showError : function(msg){
				$rootScope.errorMessage = msg;
				$rootScope.$broadcast('errorOccured');
			},
			showSuccess : function(msg){
				$rootScope.successMessage = msg;
				$rootScope.$broadcast('eventSuccess');
			}
		};
	};
	angular.module('ygVendorApp')
	.factory('Notification', [
		'$rootScope',
		'$state',
		'$document',
		Notification
	]);

})();