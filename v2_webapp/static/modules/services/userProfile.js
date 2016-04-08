(function(){
	'use strict';
	var UserProfile = function ($q,role,Profile){
		var userProfile = {};
		var fetchUserProfile = function() {
			var deferred = $q.defer();
			Profile.profile(function (response) {
				if (userProfile.hasOwnProperty('role')) {
					delete userProfile.role;
				}
				if (userProfile.hasOwnProperty('name')) {
					delete userProfile.name;
				}
				if (userProfile.hasOwnProperty('is_authenticated')) {
					delete userProfile.is_authenticated;
				}
				deferred.resolve(angular.extend(userProfile, response, {
					$refresh: fetchUserProfile,
					$getUsername: function(){
						return userProfile.name;
					},
					$getUserRole: function(){
						return userProfile.role;
					},
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