(function(){
	'use strict';	
	var orderDetailCntrl = function($state,$stateParams,$rootScope,order,DeliveryGuy,Order,orderDgAssign,OrderStatusUpdate,PreviousState,constants,$q){
		var s3 = new AWS.S3();
		var self = this;
		self.params = $stateParams;
		self.order = order.payload.data;
		console.log(self.param );

		function drawConvertedImage(bufferStr , name) {
			var image_proof = new Image();
			var ctxImageWidht;
			var ctxImageHeight;
			image_proof.src = "data:image/png;base64,"+ bufferStr;
			image_proof.onload = function(){
				var canvas = document.createElement('canvas');
				var context = canvas.getContext('2d');
				if(image_proof.width >= image_proof.height){
					ctxImageWidht = 1024;
					ctxImageHeight = 768;
				}
				else{
					ctxImageWidht = 768;
					ctxImageHeight = 1024;
				}
				context.canvas.width = ctxImageWidht;
				context.canvas.height = ctxImageHeight;
				context.drawImage(image_proof, 0,0 ,image_proof.width ,image_proof.height, 0, 0, ctxImageWidht ,ctxImageHeight);
				var link = document.createElement('a');
				var evt = document.createEvent("HTMLEvents");
				evt.initEvent("click");
				link.href = canvas.toDataURL();
				link.download = name+'.png';
				link.dispatchEvent(evt);
			};
		}
		function convertBinaryToImage (data){
			var deferred = $q.defer();
			var str = "", array = new Uint8Array(data.Body);
			for (var j = 0, len = array.length; j < len; j++) {
				str += String.fromCharCode(array[j]);
			}
			var base64string = window.btoa(str);
			if(base64string){
				deferred.resolve(base64string);
			}
			else {
				deferred.reject('error creating base64 data');
			}
			return deferred.promise;
		}
		function getS3Images (img , cb){
			s3.getObject({Bucket : constants.S3_BUCKET,Key: img.Key}, function (err, data){
				if(err){
					cb(err);
				}
				else{
					var base64ConvertedData = convertBinaryToImage(data);
					base64ConvertedData.then(function (bs64data){
						drawConvertedImage(bs64data,img.Key);
						cb();
					},function (err){
						cb(err);
					});
				}
			});
		}
		var _safari = function(){
			var isSafari = /Safari/.test(navigator.userAgent) && /Apple Computer/.test(navigator.vendor);
			if(isSafari){
				var test_popup = window.open('');
				if(test_popup === null || typeof(test_popup) === undefined){
					return true;
				}
				else{
					return false;
				}
			}
			else{
				return false;
			}
		};
		/*
			function to redirect back to the previous page or parent page.
		*/
		self.goBack = function(){
			if(PreviousState.isAvailable()){
				PreviousState.redirectToPrevious();
			}
			else{
				$state.go('home.opsorder');
			}
		};
		self.downloadPop = function(){ 
			var param = {
				Bucket : constants.S3_BUCKET,
				Prefix : self.param.id+'/'+self.order.pickedup_datetime.slice(0,10)+'/pop'
			};
			self.download_image(param);
		};

		self.downloadPod = function(){ 
			var param = {
				Bucket : constants.S3_BUCKET,
				Prefix : self.param.id+'/'+self.order.pickedup_datetime.slice(0,10)+'/pod'
			};
			self.download_image(param);
		};

		self.download_image = function(param){
			s3.listObjects(param, function (err, data){
				if(err){
					$rootScope.errorMessage = '';
					$rootScope.$broadcast('errorOccured');
				}
				else{
					if (data.Contents.length === 0) {
						$rootScope.errorMessage = 'No Proof Found';
						$rootScope.$broadcast('errorOccured');
						return;
					}
					if( _safari() ) {
						$rootScope.errorMessage = 'To view the proofs! \nOption 1: Go to Safari —> Preferences —> Security —>  Block popup windows (Disable)\nOption 2: Use Chrome browser to download the images';
						$rootScope.$broadcast('errorOccured');
						return;
					}
					else{
						async.map( data.Contents , getS3Images , function(err, result) {
							if(err){
								$rootScope.errorMessage = err;
								$rootScope.$broadcast('errorOccured');
							}
							else {
								console.log(result);
							}
						});
        			}// end of else
      			} // end of else 
    		}); // end of listObject
		};
		/*
			@assignDgForSingleOrder is a function to open dg assignment dialog box and assign delivery guy and pickup guy for the 
			order once user confirms things.
		*/
		self.assignDgForSingleOrder = function(order){
			orderDgAssign.openDgDialog()
			.then(function(assign_data) {
				assign_data.pickup.delivery_ids = [order.id];
				assign_data.delivery.delivery_ids = [order.id];
				self.assignOrders(assign_data);
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
				self.getOrder();
			});
		};

		self.updatePickupStatus = function(status_data){
			var array = [];
			for(var i=0; i< status_data.delivery_ids.length;i++){
				status_data.data.id = status_data.delivery_ids[i];
				array.push(Order.updatePickup.update(status_data.data).$promise);
			}
			$q.all(array).then(function(data){
				self.getOrder();
			});
		};
		self.updateDeliveryStatus = function(status_data){
			var array = [];
			for(var i=0; i< status_data.delivery_ids.length;i++){
				status_data.data.id = status_data.delivery_ids[i];
				array.push(Order.updateDelivered.update(status_data.data).$promise);
			}
			$q.all(array).then(function(data){
				self.getOrder();
			});
		};
		self.statusUpdateDialog = function(order){
			OrderStatusUpdate.openStatusDialog()
			.then(function(status_data) {
				status_data.delivery_ids = [order.id];
				if(status_data.isPickup){
					self.updatePickupStatus(status_data);
				}
				else{
					self.updateDeliveryStatus(status_data);
				}
			});
		};
		/*
			@getOrder rleoads the order controller according too the filter to get the new filtered data.
		*/
		self.getOrder = function(){
			$state.transitionTo($state.current, self.params, { reload: true, inherit: false, notify: true });
		};
	};

	angular.module('order')
	.controller('orderDetailCntrl', [
		'$state',
		'$stateParams',
		'$rootScope',
		'order',
		'DeliveryGuy',
		'Order',
		'orderDgAssign',
		'OrderStatusUpdate',
		'PreviousState',
		'constants',
		'$q',
		orderDetailCntrl
	]);

})();