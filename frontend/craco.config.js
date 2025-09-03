const path = require('path');

module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      // Remove ALL problematic plugins that use schema-utils
      webpackConfig.plugins = webpackConfig.plugins.filter(plugin => {
        const pluginName = plugin.constructor.name;
        return !pluginName.includes('ForkTsCheckerWebpackPlugin') &&
               !pluginName.includes('TerserPlugin') &&
               !pluginName.includes('OptimizeCssAssetsPlugin');
      });
      
      // Disable TypeScript checking completely
      webpackConfig.resolve.extensions = ['.js', '.jsx', '.json'];
      
      // Add fallbacks for Node.js modules
      webpackConfig.resolve.fallback = {
        ...webpackConfig.resolve.fallback,
        "path": require.resolve("path-browserify"),
        "os": require.resolve("os-browserify/browser"),
        "crypto": require.resolve("crypto-browserify"),
        "stream": require.resolve("stream-browserify"),
        "buffer": require.resolve("buffer"),
        "util": require.resolve("util"),
        "fs": false,
        "net": false,
        "tls": false
      };

      return webpackConfig;
    }
  }
};
