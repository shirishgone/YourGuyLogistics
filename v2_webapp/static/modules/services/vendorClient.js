(function(){
	'use strict';
	var vendorClients = function ($q,role,Vendor){
		var vendorClients = {};
		var fetchVendors = function() {
			var deferred = $q.defer();
			Vendor.query(function (response) {
				deferred.resolve(angular.extend(vendorClients, response, {
					$refresh: fetchVendors,
					$updateuserRole: function(){
						return role.$setUserRole();
					},
					$clearUserRole: function(){
						return role.$resetUserRole();
					},
					$hasRole: function(roleValue) {
						return role.$getUserRole().userrole == roleValue;
					},

					$isAuthenticated: function() {
						return role.$getUserRole().is_authenticated;
					},
					$isAnonymous: function() {
						return !role.$getUserRole().is_authenticated;
					}
				}));

			}, function (error){
				deferred.resolve(angular.extend(vendorClients ,{
					$refresh : fetchVendors,
					$updateuserRole: function(){
						return role.$setUserRole();
					},
					$clearUserRole: function(){
						return role.$resetUserRole();
					},
					$hasRole : function (roleValue){
						return role,$getUserRole().userrole == roleValue;
					},
					$isAuthenticated: function() {
						return role.$getUserRole().is_authenticated;
					},
					$isAnonymous: function() {
						return !role.$getUserRole().is_authenticated;
					}
				}));
			});
			return deferred.promise;
		};
		return fetchVendors();
	};

	angular.module('ygVendorApp')
	.factory('vendorClients', [
		'$q',
		'role',
		'Vendor', 
		vendorClients
	]);
})();