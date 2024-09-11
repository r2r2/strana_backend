from sl_auth_tokens.emitter import TokenEmitter

from src.entities.users import Language, Role

PRIVKEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAqdzb9/Rdb04hrNdn8fNt8KnbmQiyX9bMhDNrVRniq7KDg+AD
+pwKFphrphHHCr+t4JBCfY8JLxTisLh55yBRKKheah1enXiRk7OBqdNcA0XGVYF7
A9JffKqrbWtl0UGlQaA5g350J0udWCFabJBgkd7NZbQHeQXNHfyG3rS9lz2kcIuK
dj+TBY5EKP3OZqxFvp9bQIZwAIZ2Wn6uS18vCtY1MnueCcvBf/hT+c4Qz7uR/rxt
3xVORFVcFMT6RCuR+W1be3gw0pMGJCkXeEJaLD8NMfquiD6VnBDiBkSY9oU1p4CR
JBto+CFYGc0oKNVSF1UOZv1fg9PfRm7YERw42QIDAQABAoIBACsGCWMe7nGMSSRF
tQrH/R85bqku1jtHJSsQ+Q0njs2tW/lRisB1uGprtcxs8UzMKwbXkzfJPGrD7/0R
5LKBcX0KVEutX7MkAD94do2kvsgHaspqjtVzegMSGXSQAMyFQ43BPwAKzfHMCbDy
Vbxsv0EDPWQWutPQ/9iqByEuh1zgcuvgTUPw8GmGSV1ECBxldJPnEPaqHn5EneJr
lMRobPz+y2xG/vOwMTbMacTRE3rpcFbvoLt5dI+c1IwXau4W8ypVhm9utiw0+UHv
iZ4L47bzpJDg35All7K0LDi5iHxsT8EbL442ICEEwST0v4BRmZdjniYZtWTH8PYX
oSLVmG8CgYEAyU+v/c9jAw6oJ3antnHmx3QSBS1scKJRoKG60ca7dI3YExHzoztJ
6zpMcj4kMk9SGSIEG9sEaj+VhgsVW7BSqaG5LnyaaVKrNECANjJ1KBieSwW/25wc
kvRkWhRCUy9oL7jkeoAPL6U/RkPXorte8mku7SSvkqkap7N+Le1sVhMCgYEA2AIQ
WFAfziG3JUk0gYuFn3VwWjRF+Ks3F4MWvLXJd9PEz3iP40MM1p6KIxauBVWznDgq
iMNQLMlz7voGffmYx0H4l4xBHJuny50nHAWlMbly+kFOGj3oCngs+7iUoCMIUuu0
HRi4o2kXwG08klun7S+3BTvMRwF1cstmMXwZQuMCgYA7bOyUze16b48v5xTnBISN
iDPxl1EVhrT16AgP+MxJQb3xEzGKk+vkJld+ud1RhJzFkocH+gU5n/9xjEAHyur7
7COQF3Q1dxPW3tt6JDb1WR8RImdaWqEMuFwPQz+48pucysWXa8oP1IXzJf+3p/wF
LwuNMXEqqASYUKIEyLtcRQKBgGsL6sm5O2nN75M8yhaA7EFv07QAP8TSJMU0I6p1
dFg7zEb8+mGnss8RVme5L5hZNl9uvjV0hWEMnLWLlngLn5jvqqB/0yy4Ptl7Egyj
B5Cy1LYMcwYyM7IsiC5e9Ni/Q7rEMEhTHf1tcWXdPK1TWs8CXHLthXiS0n+HKSfQ
1jv9AoGAV6KHZt9Ry52W2LidvE0BTDPE1a/6VcQd3+bggRwqXnyhblu8YGVBu25O
JLUTjB1DzEPn2LDMUF7YPX3K0ktP22Ek1NwelIft3FBY5saxZazHv0/lQhHSXd6+
GC9neVDGwqgD3SMSZ7izzLLglMwvkgXTounfFO+Mubc8gpkHLJk=
-----END RSA PRIVATE KEY-----"""


def generate_auth_token(user_id: int, roles: list[Role], lang: Language, audience: list[str]) -> str:
    emitter = TokenEmitter(private_key=PRIVKEY, issuer="auth", algorithm="RS256")
    return emitter.emit(
        subject=f"user_{user_id}",
        audience=audience,
        ttl=360000,
        user_id=user_id,
        roles=[role.value for role in roles],
        lang=lang.value,
    )
