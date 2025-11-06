export default function WorkingPage() {
  return (
    <html>
      <body style={{ padding: '40px', fontFamily: 'system-ui' }}>
        <h1>✅ SUCCESS! Next.js is working!</h1>
        <p>This page proves the Next.js app itself works fine.</p>
        <p>The problem is with the [locale] dynamic route configuration.</p>
        <hr />
        <h2>Diagnosis:</h2>
        <ul>
          <li>✅ Next.js routing: WORKING</li>
          <li>✅ Vercel deployment: WORKING</li>
          <li>❌ [locale] dynamic routes: NOT WORKING</li>
        </ul>
        <hr />
        <h2>Next Steps:</h2>
        <p>We need to either:</p>
        <ol>
          <li>Downgrade to Next.js 14.x</li>
          <li>Restructure the app without [locale] folders</li>
          <li>Use a different i18n approach</li>
        </ol>
      </body>
    </html>
  );
}
