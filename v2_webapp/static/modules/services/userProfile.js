(function(){
	'use strict';
	var UserProfile = function ($q,role,Profile){
		var userProfile = {};
		var fetchUserProfile = function() {
			var deferred = $q.defer();
			Profile.profile(function (response) {
				deferred.resolve(angular.extend(userProfile, response, {
					$refresh: fetchUserProfile,
					$clearUserRole: function(){
						return role.$resetUserRole();
					},
					$hasRole: function(roleValue) {
						return userProfile.role === roleValue;
					},
					$hasAnyRole: function(roles) {
						return roles.indexOf(userProfile.role) >= 0;
					},
					$isAuthenticated: function() {
						return userProfile.is_authenticated;
					},
					$isAnonymous: function() {
						return !userProfile.is_authenticated;
					}
				}));

			}, function (error){
				userProfile = {};
				deferred.resolve(angular.extend(userProfile ,{
					$refresh : fetchUserProfile,
					$clearUserRole: function(){
						return role.$resetUserRole();
					},
					$hasRole : function (roleValue){
						return userProfile.role == roleValue;
					},
					$hasAnyRole: function(roles) {
						return roles.indexOf(userProfile.role) >= 0;
					},
					$isAuthenticated: function() {
						return userProfile.is_authenticated;
					},
					$isAnonymous: function() {
						return !userProfile.is_authenticated;
					}
				}));
			});
			return deferred.promise;
		};
		return fetchUserProfile();
	};

	angular.module('ygVendorApp')
	.factory('UserProfile', [
		'$q',
		'role',
		'Profile', 
		UserProfile
	]);
})();