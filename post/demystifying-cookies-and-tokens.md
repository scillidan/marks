```
Date: 2024.05
Author: Tommi Hovi
Source: https://tommihovi.com/2024/05/demystifying-cookies-and-tokens/
```

# Demystifying cookies and tokens

I have been recently diving head first into the world of tokens and cookies. One of my customer’s is trying to prevent token and cookie theft and it has got me digging more information and deeper. I bet you have heard these terms and most likely you’re using them daily. But there are variations of tokens and cookies and some context around them that we should understand to see the bigger picture. Here’s what I’ve learned so far! Let’s start!

## Setting the goal

In this blog post we will reach and understanding of what web cookies and tokens are and what are they used for. We will also look at the most common types of web cookies and tokens. This post is not going into how to prevent token or cookie abuse. That’s a topic for another post.

## What are cookies?

Let’s first begin by trying to understand what web cookies are and how do we use them. The general term cookies in this article refers to a web cookie.

### Cookies explained

**Cookies are small text files** that are created by the websites (web servers) you visit and stored in your device. We’ve all ran into them. Practically every website you visit is “greeting” you with a cookie banner. The purpose of the cookie depends on the type of cookie and what the website wants the cookie to do. Example, an online store could use cookies to track users’ movements on their site, what was the last page they visited, what language you’ve selected, what items the user had looked at and what items he had placed in the shopping cart. When user leaves the website, but later returns, the website can read the cookie and for example pick up where the user left off. But not all cookies serve the same purpose.

The following picture explains in very high level how cookies work.

![](assets/demystifying-cookies-and-tokens_01.png)  
Image 1. High-level definition of how cookies come to life  
Source: Cookieyes. Check source URL from lower left corner of picture

But why do we need cookies in the first place? **We need cookies, because HTTP is a stateless protocol.** HTTP does not remember client session information and thus the client is responsible for storing that information – using a cookie. For some websites stateless behavior might be okay, maybe there are no elements or user actions that the website should retain during user’s session. But for most interactive websites, cookies are necessary and essential and also we, as website visitors, are expecting websites to behave in a certain manner. Many thanks to cookies which makes it possible. When the client requests a website from the webserver, the webserver responses with **‘200 OK’** and sends a cookie to the client using the **Set-Cookie** header. The cookie contains the session ID and typically contain other attributes also. The webserver also keeps track of session IDs that the site has handed out to clients on server side.

Cookies are primarily used for:

1. HTTP session management
2. Personalization
3. Tracking

**Cookies are stored on your browser.** To be more exact they are stored in browser’s temporary directory on your hard drive. The exact locations and methods for storing cookies depend on the browser and the operating system. You would most typically manage your cookies via the browser interface by going into the settings, but folder paths for different operating systems and browser are available in the internet. For example, Microsoft Edge stores cookies in the following path:

- **C:\\Users\\\[username\]\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Network**

![](assets/demystifying-cookies-and-tokens_02.png)  
Image 2. Such files should be expected when browsing to the file path

Typically you would use the browser’s interface to manage, view or remove cookies.

![](assets/demystifying-cookies-and-tokens_03.png)  
Image 3. Microsoft Edge cookies in browser settings

#### Cookie attributes

Cookies have attributes (_sometimes also referred to as flags_) that are quite important as they define how the cookie works. Here is a list of some attributes that cookie can have.

- _Session ID_ is a unique random string used to identify and match the session between the client and the webserver
- _Expires_ defines the date when the cookie is set to expire
- _Domain_ specifies the domain or domains where the cookie is valid to be used
- _Path_ specifies the resource or path where the cookie is valid to be used
- _HttpOnly_ when enabled will prevent client side APIs such as JavaScript from accessing the cookie. This mitigates the threat of cross-site scripting (XSS).
- _Secure_ when enabled will require the cookie to be sent only using HTTPS while unencrypted connections like HTTP are not allowed which makes the cookie less vulnerable to the cookie theft.
- _Session_ defines that the cookie is a temporary cookie which expires when the browser is closed
- _SameSite_ can have values **strict**, **lax** or **none**
  - Strict = browser sends cookies only to target domain that is same as origin domain
  - Lax = browser send cookies to target domain even if it is different from the origin domain, but only for safe request (like GET) and not third-party cookies.
  - None = allows third-party cookies (cross-site cookies)

You can see the cookies of the site you’re browsing by right-clicking and selecting the ‘_Inspect_‘ > ‘_Application_‘ > ‘_Storage_‘ > ‘_Cookies_‘. When you select a row, you can see the values on the bottom of the page (_see the Image 5._)

![](assets/demystifying-cookies-and-tokens_04.png)  
Image 4. Website ‘Inspect’ will let you see the cookies for that specific website and the cookie consent user has accepted to

![](assets/demystifying-cookies-and-tokens_05.png)  
Image 5. Cookie consent is also visible

![](assets/demystifying-cookies-and-tokens_06.png)  
Image 6. The result of opening Google Chrome which opens www.google.com website by default and checking active cookies!

### Types of cookies

Here’s some cookie terminology that you might run into when you have to play around with cookies. Cookies can be divided into rough categories in multiple ways. There are first-party cookies and third-party cookies. There are essential cookies (strictly necessary) and non-essential cookies (non-necessary). We will use the latter definition here to categorize our cookies. The categorization doesn’t really matter, it’s just easier for humans to put stuff in mental boxes. Also some cookies are just variations of other cookies. For example, you might hear about ‘secure cookie’ but in fact that might just be a session or first-party cookie that has _secure_\-attribute enabled. And even then session cookies and first-party cookies can be really similar. Even if the terminology is quite vague to my opinion and different sites use different cookie terms interchangeably, let’s still at least try to give some sort of definition to each of them.

#### Essential cookies

Essential cookies are necessary for the website to function properly and often make the browsing experience more convenient for the user.

- Session cookies
- First-party cookies
- Authentication cookies
- User-centric security cookies
- User-input cookies

##### Session cookies _(a.k.a. non-persistent cookie, in-memory cookie, transient cookie)_

**Session cookies are temporary cookie files**, which are removed when user closes the browser or their session becomes inactive (if user logs out the session will end). They are single sessions cookies. When user restarts their browser and goes back to the site that created the cookie, the website will not recognize the user because there’s no cookie for the website to read in user’s browser. User will have to log back in (if login for the website is required). Upon logon, a new session cookie will be generated, which will store user’s browsing information and will be active until the user leaves the site and closes the browser. As the session cookie has its own unique id, it can also be used to track website visitor count. If you’re planning a vacation trip and your visit a travel agency’s website multiple times a day, the session ID of the cookie will reveal to the site that you’re just one unique visitor.

##### First-party cookies _(a.k.a. persistent cookies, permanent cookies, stored cookies)_

**First-party cookies will stay** in a browser **until a user deletes them or a browser deletes them** based on the duration period contained within the persistent cookie’s file. This type of cookie can be referred to in other terms such as persistent cookie, permanent cookie or stored cookie and thus they have persistence over a single session. Most first-party cookies will expire within 1-2 years if the site is not visited during that time. When cookie expires the browser will remove them automatically. A first-party cookie is most known to serve users in keeping their accounts logged in to the websites and thus avoiding the tedious re-entering of credentials at each visit of the site.

##### Authentication cookies

**Authentication cookies** are a variation of a session cookies. They **will identify user after successful login** and carry that authentication information as the user navigates on a website where the content is authorized to the logged in user. For example, when user authenticates to an online bank, they are authorized to see their bank account balance. If they move on to another page to view their loans the authentication cookie makes sure that the user does now have to provide new authentication for that page.

##### User-centric security cookies

**User-centric security cookies** can keep track of authentication errors and **detect possible authentication abuse** by keeping track how many times incorrect login credentials had been tried on login page.

##### User-input cookies

**User-input cookies** are first-party session cookies that **keep track of the actions and items that the users themselves are inputting** on the website, like filling in a form or clicking some buttons (like add to shopping cart).

#### Non-essential cookies

Non-essential cookies are not necessary for the user’s browsing experience or the website to function properly.

- Analytics and customization cookies
- Advertising cookies
- Third-party cookies
- Supercookies

##### Analytics and customization cookies

Analytics and customization cookies track users activity to allow website admins to better understand how their site is being used. An example of an analytic that website admins could use to enhance the site is that some information on the website might be really “cold”, meaning that users rarely open that page (not interested) or cannot find their way into it.

##### Advertising cookies

Advertising cookies are simply used to customize the ads users see on webpages. They use the user’s browsing history to make the ads “more relevant”. This is why we start seeing ads about something we’ve searched for previously.

##### Third-party cookies (a.k.a. tracking cookies)

**Third-party cookies are the bad guys** of the “cookieland”. These are the cookies that we don’t like and the reason that the cookies have such lousy reputation. Third-party cookies originate from a different domain that the user is visiting, thus they do not provide any benefits of session cookies or first-party cookies. **These cookies serve for one purpose only which is to track you**.

##### Supercookies

Supercookies are not technically cookies and in some cases are are not stored on user’s device. Whereas “normal” cookie can hold up to 4 KB of data, a supercookie can hold a 100 KB. Supercookies serve a similar function to tracking cookies, but they are not controlled the same way as other cookies. In some cases supercookies have been found stored in browser cache and some forms of supercookies are injected into UIDHs (unique identifier headers) that ISPs only control. Due to the nature of a supercookie, they are harder to identify and in case of UIDH supercookie there’s no way for you to clear them.

___

## What are tokens?

Tokens are self-contained and compact JSON objects for information exchange. A typical token is a JSON Web Token (JWT) that is used between the client (application) and another service (like a web server). The details depend on the exact authentication flow. In this post we will use term JWTs (pronounced as ‘JOT’) as it is more convenient and widely used in professional literature.

### Tokens explained

Unlike cookies which store information about the user’s activities in a web session short or long-term, tokens transport information between software. The information stored in a token depends on the type of a token. For example ID token carries information about the authenticated user. Access token usually contains information about the security principal and what access is it authorized for. **Here’s where tokens and cookies intersect**: some tokens are stored on client-side either in a place called Local Storage or in a cookie. Most preferably in a HttpOnly cookie for security reasons. I’m not a web developer, but I’ve let myself understand that the developer community is leaning towards cookies, as the Local Storage is deemed to be less secure option. It’s also worth mentioning that tokens are used as part of a protocol and not all tokens are part of the same protocol.

The protocols I will mention and shortly explain here are **OAuth 2.0** and **OpenID Connect** (OIDC), because they are used by **Microsoft Identity Platform**.

**OAuth** is short from Open Authorization and it is a standard designed to handle authorization flow of an application or website accessing resources on behalf of the user. In simple terms, OAuth is an authorization protocol mainly used in web platforms. OAuth uses access tokens, which are typically, but not limited to, JSON Web Tokens. OAuth protocol in Microsoft Identity Platform uses access tokens (bearer tokens) that are formatted as JWTs. There are multiple different types of OAuth 2.0 authorization flows.

**OpenID Connect** extends OAuth 2.0 authorization protocol so that it is also used as an authentication protocol which uses ID token. OpenID Connect sign-in flow is used to acquire ID token which is sent to the application that validates the user identity.

![](assets/demystifying-cookies-and-tokens_07.svg)  
OpenID Connect sign-in flow. Source: Microsoft Learn

![](assets/demystifying-cookies-and-tokens_08.svg)  
After sign-in flow access token is acquired via OAuth authorization flow. Source: Microsoft Learn

### The problem tokens are solving

Let’s describe a traditional authentication and authorization scenario where tokens do not exist. User first logs in and the web server authenticates the user by checking the entered credentials from its database. Once credentials match, server then issues an unique session identifier and sends it to the client. User’s client stores the session id on the device. For each subsequent request from the client to the server, the session id is sent in a cookie or in a http request header. The server needs to look up the session id again from its database to identify the user and check authorization level.

The problem with the above scenario is that for every request from the client the server needs to make a round trip to the database which makes the application slower to use.

Whereas the scenario with tokens solves the subsequent database lookups by issuing a JWT that contains the user information and signature that verify the authenticity of the tokens contents. JWT is sent to the client which again stores it. For each request from the client to the server, the client includes the JWT. Server just needs to validate the token’s signature to ensure its authenticity and when that checks in, the server can extract the identity and authorization details from the token with out database lookups.

### Types of tokens

Here are some common token types:

- ID token
- Access token
- Refresh token
- Bearer token

Next I will introduce these tokens and terms briefly.

##### ID token

ID tokens are acquired using the OpenID Connect (OIDC) sign-in flow, which is an open standard for decentralized authentication. ID tokens are required to be in the JSON Web Token format. They are issued by the authorization server (Microsoft Entra ID) to the client application. **ID token contains claims about the user** or security principal and can contain claims about MFA status for example. Client application can verify that the user is who they claim to be using the information and claims in the ID token. By default ID tokens are valid for an hour in Microsoft Identity Platform. **ID tokens are not used for calling protected APIs.**

Microsoft has two versions of ID tokens and both have different endpoints. The difference between the versions is in the information and the claims they can contain.

- v1.0 **https://login.microsoftonline.com/common/oauth2/authorize**
- v2.0 **https://login.microsoftonline.com/common/oauth2/v2.0/authorize**

![](assets/demystifying-cookies-and-tokens_09.jpg)

User is signing in to the web application that redirects the user to Entra ID to complete authentication. Once successfully authenticated Entra ID will issue an ID token and sends it to the client (browser). The browser doesn’t try to make sense of the ID token and just sends it over to the web server.

##### Access token

**Access token** is a short-lived (JWT) token signed by the authorization server and **enables clients to securely call protected web APIs**. Access tokens are not required to be formatted as JSON Web Tokens, but in Microsoft Identity Platform they are in JWT format. Access tokens are included in every http request from clients to the server. This typically happens via the Authorization header in the http request using the ‘Bearer’ schema. Doing so will avoid the need for the server to authenticate the user on each request. The client stores the access token either in a cookie or in a local storage. Like ID tokens, access tokens too have two versions which both have distinct endpoints. Access tokens are meant to be consumed server-side. Client-side does not need and should not be used to read the contents of the access token.

##### Refresh token

**Refresh token is** typically acquired alongside the access token. It is **used to acquire a new access tokens** when the previous access tokens expire and also new refresh token. In Microsoft Identity Platform refresh tokens are encrypted and cannot be read by none other. The client stores the access token either in a cookie or in a local storage. Default lifetime of a refresh token is 90 days, single page apps being the exception where the default lifetime is 24 hours.

##### Bearer token

Bearer token is a term used for tokens that can be used by anyone that has the possession of the token. The token bearer does not have to proof the possession of cryptographic key. Think of it like a hotel room keycard. If you misplace the keycard and someone else gets the possession of it, they can use it to enter the hotel room without them needing to prove that they are the rightful owner of the room.

## JSON Web Token (JWT)

JSON Web Tokens are a standardized objects that are used to securely send data between two parties. To ensure that the contents of JWT has not been altered or tampered during the transmission of it, the JWT is signed using cryptographic key. This needs to be repeated: **JWTs are signed, NOT encrypted**. Signing verifies the sender of the data whereas encryption transforms the data from plaintext to ciphertext that cannot be read by unauthorized recipient. If signed token content would be changed during transmission the public key (which is the pair of the private key used to sign the token) would not be able to verify the signature anymore. It is strongly recommended to use protocols such as HTTPS with JWTs to protect the confidentiality of the token contents during transit.

Internet Engineering Task Force (IETF) describes the JWT standard in [RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519).

JSON Web Token consist of three parts:

- Header
- Payload
- Signature

#### Header

Typically the header consists of two parts that describe the **type of the token** and the **signing algorithm**.

```
{
  "alg": "HS256",
  "typ": "JWT"
}
```

#### Payload

Payload is the part that contains all the actual information e.g. **claims**. In Chapter 4 of RFC 7519, Registered Claims are defined as following:

- **“iss”** = Issuer Claim. Issuer claim identifies the principal that issued the JWT
- **“sub”** = Subject Claim. Subject claim identifies the principal that is the subject of the JWT
- **“aud”** = Audience Claim. Audience claim identifies the recipients that the JWT is intended for
- **“exp”** = Expiration Time Claim. Expiration claim identifies the expiration time on or after which the JWT must not be accepted for processing
- **“nbf”** = Not Before Claim. NFB claim identifies the time before which the JWT must not be accepted for processing
- **“iat”** = Issued At Claim. Issued At claim identifies the time at which the JWT was issued
- **“jti”** = JWT ID Claim. The JWT ID claim provides a unique identifier for the JWT

The standard does not enforce the use of the registered claims, therefore they remain optional. Other types of claims are **Public Claim Names** and **Private Claim Names**.

```
{
  "session": "ch72gsb320000udocl363eofy",
  "client_id": "YzEzMGdoMHJnOHBiOG1ibDhyNTA=",
  "response_type": "code",
  "scope": "introscpect_tokens, revoke_tokens",
  "iss": "bjhIRjM1cXpaa21zdWtISnp6ejlMbk44bTlNZjk3dXE=",
  "sub": "YzEzMGdoMHJnOHBiOG1ibDhyNTA=",
  "name": "John Doe",
  "aud": "https://login.microsoftonline.com/{tid}/oauth2/v2.0/authorize",
  "jti": "1516239022",
  "exp": "2024-05-17T07:09:48.000+0545"
}
}
```

#### Signature

The header and payload are both **Base64Url** encoded. To sign the token, encoded header and encoded payload are used along with the secret and the signing algorithm to complete the signature.

```
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret)
```

The following screenshot shows the signed JWT on the left side and the Header, Payload and Signature on the right side.

![](assets/demystifying-cookies-and-tokens_10.png)  
You can see the all the three parts of JSON Web Token in a signed JWT where the different parts are separated by a dot (.)

### Example token

Easiest way to review a JWT is going to Microsoft Graph Explorer [https://developer.microsoft.com/en-us/graph/graph-explorer](https://developer.microsoft.com/en-us/graph/graph-explorer) and signing in. After signing in, we run the ‘**GET my profile**‘ query and open the **Access token** tab and copy the token.

![](assets/demystifying-cookies-and-tokens_11.png)  
Parts of access token redacted for security hygiene reasons

Then we head over to [https://jwt.ms](https://jwt.ms/) and paste in the token.

![](assets/demystifying-cookies-and-tokens_12.png)  
Parts of access token redacted for security hygiene reasons

Below the token we’ve pasted is the token contents decoded and the ‘Claims’ tab that explains the claim acronyms like “oid”, “uti” and so on. From the below token we can deduce the following:

- **“typ”: “JWT”** indicates the token type is JSON Web Token
- **“alg”: “RS256”** means that the signature of this token uses RSA Signature with SHA-256 algorithm
- **“aud”: “00000003-0000-0000-c000-000000000000”** means that the token recipient (_audience_) is **Microsoft Graph**
- **“iss”: “https://sts.windows.net/f77b793c-9409-XXXX-XXXX-b793feaadb48/”** indicates that the issuer of the token is Azure Active Directory v1 endpoint
- **“appid”: “de8bc8b5-d9f9-48b1-a8ad-b748da725064”** means that the client using the token is **Graph Explorer** as it uses the token to call the Microsoft Graph API
- **“scp”: “openid profile User.Read email”** lists the API scopes that are the application (Graph Explorer) has requested and what has been consented and what the Microsoft Graph has exposed
- **“ver”: “1.0”** indicates the token version

![](assets/demystifying-cookies-and-tokens_13.png)

```
**Psst!** I noticed that the issuer for all the tokens I acquired was **sts.windows.net**. I assumed it would be **login.microsoftonline.com**. Quick research points to the **accessTokenAcceptedVersion** parameter which seems to control the token issuance endpoint. This needs more testing later to state as a fact, but here’s how it seems to work:  
Value **null** defaults to version 1.0  
Value **1** means also version 1.0 (sts.windows.net)  
Value **2** means version 2.0 (login.microsoftonline.com)
```

![](assets/demystifying-cookies-and-tokens_14.png)  
App Registration Manifest configuration

### Security concerns of JWT

Like any technical solution, JSON Web Token too have its downsides.

##### Size constraints and storing

Some complex applications need store a lot of information in a token. When tokens are stored in cookies this can increase the per request overhead or even exceed the allowed size for a cookie (4 KB). When this happens a common workaround is to store the JWT in a **Local Storage** which has its own security issues, mainly the data in local storage being accessible for any script inside the page. This can lead to cross-site scripting (XSS) attack being able to access the token.

In general, cookies are meant to be read by the server whereas Local Storage can only be read by the browser. This means that the cookie is restricted to smaller data volumes than local storage. When token is stored in a local storage the browser uses JavaScript to access it. This is the root cause why tokens stored in local storage are vulnerable to cross-site scripting as an attacker could inject malicious JavaScript into a webpage and steal the access token. Local storage does not provide any security measures that cookies have in secure attributes. Don’t get me wrong, if token is stored in a cookies that is not properly secured then we’re also vulnerable to XSS attacks. But cookies have mechanisms to protect tokens from these types of attacks and that’s why OWASP community also recommends storing tokens using cookies.

##### Invalidation

As stated in the beginning, tokens are self-contained. There is no central authority that tracks and manages the tokens. This becomes a challenge when trying to invalidate a token. By default an access token lifetime is one (1) hour and details of the expiration is contained in the token.

##### Unencrypted

Remember that tokens are signed, but not encrypted. Thus the token contents might be exposed to unauthorized parties if not adequately protected with HTTPS.

## Summary

We went through what cookies are and how browsers and websites use cookies to enhance the browsing experience. We listed some variations of cookies and their unique characteristics. We also went through what tokens are, what protocols are used in Microsoft Identity Platform to acquire tokens and in which situation is each type of token relevant. With this baseline knowledge of cookies and tokens we’re able to continue our journey in upcoming blog posts about how to compromise cookies or tokens and abuse them. Later on, we will also cover how to protect from cookie stealing and token theft!

Stay secure!