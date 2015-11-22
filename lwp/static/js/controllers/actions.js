angular.module("LWP").controller("actionsCtrl", function ($rootScope, $scope, $interval, API) {
	function update() {API.asyncTasks().then(function (data) {$scope.tasks = data});}

	var updateInterval = $interval(update, 10000);

	$scope.$on('$destroy',function(){
		$interval.cancel(updateInterval);
	});

	$scope.labelText = function (action) {
		if (action.state === null) {
			return 'processing';
		}

		return action.state?'done':'fail';
	};

	$scope.labelClass = function (action){
		if (action.state === null) {
			return 'label-info';
		}

		return action.state?'label-success':'label-danger';
	};

	update();
});