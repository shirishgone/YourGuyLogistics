(function(){
	'use strict';
	var vendorClients = function ($q,Vendor){
		var vendorClients = {};
		var fetchVendors = function() {
			var deferred = $q.defer();
			Vendor.profile(function (response) {
				deferred.resolve(angular.extend(vendorClients, response, {
					data: "vendor",
					$refresh: fetchVendors

					// $hasRole: function(role) {
					// 	return userProfile.roles.indexOf(role) >= 0;
					// },

					// $hasAnyRole: function(roles) {
					// 	return !!userProfile.roles.filter(function(role) {
					// 		return roles.indexOf(role) >= 0;
					// 	}).length;
					// },

					// $isAnonymous: function() {
					// 	return userProfile.anonymous;
					// },

					// $isAuthenticated: function() {
					// 	return !userProfile.anonymous;
					// }

				}));

			});
			return deferred.promise;
		};
		return fetchVendors();
	};

	angular.module('ygVendorApp')
	.factory('vendorClients', [
		'$q',
		'Vendor', 
		vendorClients
	]);
})();