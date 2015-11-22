angular.module("LWP").controller("navBarCtrl", function ($rootScope, $scope, $location, $interval, API) {
	$scope.hostname = '';

	API.hostname().then(function (data){
		$scope.hostname = data.hostname;
	});
});