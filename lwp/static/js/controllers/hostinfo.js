angular.module("LWP").controller("hostInfoCtrl", function ($rootScope, $scope, $location, $interval, API) {
	function hostInfo() {
		API.hostInfo().then(function (data) {
			$scope.hostInfo = data;
		});
	}

	$scope.memUsage = function () {
		if (!$scope.hostInfo) { return '0%'; }
		var total = $scope.hostInfo.memory.memtotal;
		var free = $scope.hostInfo.memory.memfree;
		return Math.floor((free * 100) / total) + '%';
	};

	$scope.cpuUsage = function () {
		if (!$scope.hostInfo) { return '0%'; }
		return Math.floor($scope.hostInfo.cpu) + '%';
	};

	var infoInterval = $interval(hostInfo, 5000);

	$scope.$on('$destroy',function(){
		$interval.cancel(infoInterval);
	});

	hostInfo();
});