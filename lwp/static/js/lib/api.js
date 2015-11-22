angular.module("LWP").factory('API', function($http, $q, $rootScope, modals) {
	function rest(url, method, data, handleErrors) {
		method = method || 'get';
		data = data || null;
		handleErrors = (typeof handleErrors === 'undefined')?true:handleErrors;

		var defer = $q.defer();

		var cllee = $http[method];
		var params = [url];

		if (data) {
			params.push(data)
		}

		$rootScope.loader[url] = false;

		cllee.apply(cllee, params).then(
			function (response) {
				$rootScope.loader[url] = true;
				defer.resolve(response.data);
			},
			function (response) {
				$rootScope.loader[url] = true;
				if (handleErrors) {
					modals.error("Error when processing " + url, response.data.error.message);
				}
				defer.reject(response);
			}
		);

		return defer.promise;
	}

	return {
		hostname: function () {
			return rest('/api/host/name', 'get');
		},
		hostInfo: function () {
			return rest('/api/host/info', 'get');
		},
		containers: function () {
			return rest('/api/container', 'get');
		},
		containerAction: function (name, action) {
			return rest('/api/container', 'put', {name: name, action: action});
		}
	};
});