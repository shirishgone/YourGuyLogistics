(function(){
	'use strict';
	var DgList = function ($q,DeliverGuy){
		var deliveryguy = {};
		var fetchdg = function() {
			var deferred = $q.defer();
			DeliverGuy.dgListQuery.query(function (response) {
				deferred.resolve(angular.extend(deliveryguy, {
					dgs : response,
					$refresh: fetchdg,
				}));

			}, function (error){
				deferred.reject(angular.extend(deliveryguy , error ,{
					$refresh : fetchdg,
				}));
			});
			return deferred.promise;
		};
		return fetchdg();
	};

	angular.module('ygVendorApp')
	.factory('DgList', [
		'$q',
		'DeliverGuy', 
		DgList
	]);
})();