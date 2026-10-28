// Set by the deploy workflow when the site is served from a sub-path
// (for example the temporary github.io address). Empty on the real domain.
const prefix = (process.env.PATH_PREFIX || '').replace(/\/$/, '');

export default function (eleventyConfig) {
  if (prefix) {
    eleventyConfig.addTransform('path-prefix', function (content) {
      if (!(this.page.outputPath || '').endsWith('.html')) return content;
      return content.replace(/(\s(?:href|src)=")\/(?!\/)/g, '$1' + prefix + '/');
    });
  }

  eleventyConfig.addPassthroughCopy({ 'src/images': 'images' });
  eleventyConfig.addPassthroughCopy({ 'src/fonts': 'fonts' });
  eleventyConfig.addPassthroughCopy({ 'src/css': 'css' });
  eleventyConfig.addPassthroughCopy({ 'src/js': 'js' });
  eleventyConfig.addPassthroughCopy({ 'src/assets/favicon.ico': 'favicon.ico' });
  eleventyConfig.addPassthroughCopy({ 'src/assets/share-image.jpg': 'share-image.jpg' });
  eleventyConfig.addPassthroughCopy({ 'src/CNAME': 'CNAME' });

  eleventyConfig.addFilter('monthShort', (iso) =>
    new Date(iso + 'T12:00:00').toLocaleString('en-CA', { month: 'short' }));
  eleventyConfig.addFilter('dayNum', (iso) => new Date(iso + 'T12:00:00').getDate());
  eleventyConfig.addFilter('monthUpperDay', (iso) =>
    new Date(iso + 'T12:00:00').toLocaleString('en-CA', { month: 'long', day: 'numeric' }).toUpperCase());

  return {
    dir: { input: 'src', output: '_site', includes: '_includes', data: '_data' },
    markdownTemplateEngine: 'njk',
    htmlTemplateEngine: 'njk'
  };
}
