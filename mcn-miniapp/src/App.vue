<script>
export default {
  onLaunch() {
    console.log('MCN管家小程序启动')
  },
  onShow() {
    console.log('小程序显示')
  },
  onHide() {
    console.log('小程序隐藏')
  },
}
</script>

<style lang="scss">
@import './static/styles/global.scss';

page {
  background-color: $bg-primary;
  color: $text-primary;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 28rpx;
  line-height: 1.6;
}
</style>
