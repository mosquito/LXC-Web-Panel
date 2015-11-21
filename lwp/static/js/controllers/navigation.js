angular.module("LWP").controller("navigationCtrl", function ($rootScope, $scope, $location, API) {
	$scope.hostname = '';

	API.hostname().then(function (data){
		$scope.hostname = data.hostname;
	});
});