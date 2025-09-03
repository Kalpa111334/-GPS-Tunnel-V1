const path = require('path');

module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      // Completely replace plugins array to avoid schema-utils issues
      webpackConfig.plugins = webpackConfig.plugins.filter(plugin => {
        const pluginName = plugin.constructor.name;
        // Only keep essential plugins that don't use schema-utils
        return pluginName.includes('HtmlWebpackPlugin') ||
               pluginName.includes('DefinePlugin') ||
               pluginName.includes('HotModuleReplacementPlugin') ||
               pluginName.includes('MiniCssExtractPlugin') ||
               pluginName.includes('ProvidePlugin');
      });
      
      // Disable all optimization that might use schema-utils
      webpackConfig.optimization = {
        minimize: false,
        splitChunks: false
      };
      
      // Disable TypeScript checking completely
      webpackConfig.resolve.extensions = ['.js', '.jsx', '.json'];
      
      // Add fallbacks for Node.js modules
      webpackConfig.resolve.fallback = {
        ...webpackConfig.resolve.fallback,
        "fs": false,
        "net": false,
        "tls": false,
        "path": false,
        "os": false,
        "crypto": false,
        "stream": false,
        "buffer": false,
        "util": false
      };

      return webpackConfig;
    }
  }
};
