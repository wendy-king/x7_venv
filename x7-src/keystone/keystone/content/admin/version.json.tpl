{
    "version" : {
        "id" : "v{{API_VERSION}}",
        "status" : "{{API_VERSION_STATUS}}",
        "updated" : "{{API_VERSION_DATE}}",
        "links": [
            {
                "rel" : "self",
                "href" : "http://{{HOST}}:{{PORT}}/v{{API_VERSION}}/"
            },
            {
                "rel" : "describedby",
                "type" : "text/html",
                "href" : "http://docs.x7.org/api/x7-identity-service/{{API_VERSION}}/content/"
            },
            {
                "rel" : "describedby",
                "type" : "application/pdf",
                "href" : "http://docs.x7.org/api/x7-identity-service/{{API_VERSION}}/identity-dev-guide-{{API_VERSION}}.pdf"
            },
            {
                "rel" : "describedby",
                "type" : "application/vnd.sun.wadl+xml",
                "href" : "http://{{HOST}}:{{PORT}}/v2.0/identity-admin.wadl"
            }
        ],
        "media-types": [
            {
                "base" : "application/xml",
                "type" : "application/vnd.x7.identity-v{{API_VERSION}}+xml"
            },
            {
                "base" : "application/json",
                "type" : "application/vnd.x7.identity-v{{API_VERSION}}+json"
            }
        ]
    }
}
