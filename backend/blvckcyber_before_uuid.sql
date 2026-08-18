--
-- PostgreSQL database dump
--

\restrict SO815wM4Q7Qmhj6W31jq7e4B13b75eyfoThHxXqPtMr5fRoaMjjmh51AQvh3JCn

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: membershiprole; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.membershiprole AS ENUM (
    'OWNER',
    'ADMIN',
    'SOC_MANAGER',
    'SOC_ANALYST',
    'INCIDENT_RESPONDER',
    'VIEWER'
);


ALTER TYPE public.membershiprole OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: memberships; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.memberships (
    id integer NOT NULL,
    user_id integer NOT NULL,
    tenant_id character varying NOT NULL,
    role public.membershiprole NOT NULL,
    is_default boolean NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    tenant_role_id integer
);


ALTER TABLE public.memberships OWNER TO postgres;

--
-- Name: memberships_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.memberships_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.memberships_id_seq OWNER TO postgres;

--
-- Name: memberships_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.memberships_id_seq OWNED BY public.memberships.id;


--
-- Name: permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.permissions (
    id integer NOT NULL,
    key character varying(150) NOT NULL,
    name character varying(150) NOT NULL,
    category character varying(100),
    description text,
    risk_level character varying(50),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.permissions OWNER TO postgres;

--
-- Name: permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.permissions_id_seq OWNER TO postgres;

--
-- Name: permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.permissions_id_seq OWNED BY public.permissions.id;


--
-- Name: pkce_attempts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pkce_attempts (
    attempt_id character varying NOT NULL,
    tenant_id character varying NOT NULL,
    code_verifier character varying NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.pkce_attempts OWNER TO postgres;

--
-- Name: role_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.role_permissions (
    role_key character varying(100) NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.role_permissions OWNER TO postgres;

--
-- Name: tenant_role_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tenant_role_permissions (
    id integer NOT NULL,
    tenant_role_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.tenant_role_permissions OWNER TO postgres;

--
-- Name: tenant_role_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tenant_role_permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tenant_role_permissions_id_seq OWNER TO postgres;

--
-- Name: tenant_role_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tenant_role_permissions_id_seq OWNED BY public.tenant_role_permissions.id;


--
-- Name: tenant_roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tenant_roles (
    id integer NOT NULL,
    tenant_id character varying(100) NOT NULL,
    key character varying(100) NOT NULL,
    name character varying(150) NOT NULL,
    description text,
    is_system boolean DEFAULT true NOT NULL,
    is_default boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.tenant_roles OWNER TO postgres;

--
-- Name: tenant_roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tenant_roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tenant_roles_id_seq OWNER TO postgres;

--
-- Name: tenant_roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tenant_roles_id_seq OWNED BY public.tenant_roles.id;


--
-- Name: tenants; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tenants (
    id character varying NOT NULL,
    name character varying NOT NULL,
    slug character varying(255) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.tenants OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    keycloak_sub character varying NOT NULL,
    email character varying,
    name character varying
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: memberships id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.memberships ALTER COLUMN id SET DEFAULT nextval('public.memberships_id_seq'::regclass);


--
-- Name: permissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions ALTER COLUMN id SET DEFAULT nextval('public.permissions_id_seq'::regclass);


--
-- Name: tenant_role_permissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_role_permissions ALTER COLUMN id SET DEFAULT nextval('public.tenant_role_permissions_id_seq'::regclass);


--
-- Name: tenant_roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_roles ALTER COLUMN id SET DEFAULT nextval('public.tenant_roles_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
4ebd48c80180
\.


--
-- Data for Name: memberships; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.memberships (id, user_id, tenant_id, role, is_default, created_at, updated_at, tenant_role_id) FROM stdin;
11	2	BLVCK-CYBER	OWNER	t	2026-08-04 09:33:29.435711	2026-08-04 09:33:29.435711	1
2	1	BLVCK-CYBER	ADMIN	t	2026-08-03 15:02:53.638969	2026-08-03 15:02:53.638969	2
12	3	BLVCK-CYBER	SOC_MANAGER	t	2026-08-04 09:33:29.435711	2026-08-04 09:33:29.435711	3
13	4	BLVCK-CYBER	SOC_ANALYST	t	2026-08-04 09:33:29.435711	2026-08-04 09:33:29.435711	4
14	5	BLVCK-CYBER	VIEWER	t	2026-08-04 09:33:29.435711	2026-08-04 09:33:29.435711	6
\.


--
-- Data for Name: permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.permissions (id, key, name, category, description, risk_level, created_at, updated_at) FROM stdin;
1	platform.all	Platform Administrator	Platform	Full platform access	critical	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
2	platform.settings.view	View Platform Settings	Platform		low	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
3	platform.settings.edit	Edit Platform Settings	Platform		critical	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
4	tenant.view	View Tenant	Tenant		low	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
5	tenant.update	Update Tenant	Tenant		high	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
6	tenant.delete	Delete Tenant	Tenant		critical	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
7	users.view	View Users	Users		low	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
8	users.create	Create Users	Users		medium	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
9	users.update	Update Users	Users		medium	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
10	users.delete	Delete Users	Users		critical	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
11	team.view	View Team	Team		low	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
12	team.invite	Invite Members	Team		medium	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
13	team.remove	Remove Members	Team		high	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
14	team.roles.manage	Manage Roles	Team		critical	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
15	alerts.view	View Alerts	Alerts		low	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
16	alerts.assign	Assign Alerts	Alerts		medium	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
17	alerts.close	Close Alerts	Alerts		medium	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
18	alerts.delete	Delete Alerts	Alerts		critical	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
19	incidents.view	View Incidents	Incidents		low	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
20	incidents.create	Create Incidents	Incidents		medium	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
21	incidents.update	Update Incidents	Incidents		medium	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
22	incidents.close	Close Incidents	Incidents		high	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
23	incidents.delete	Delete Incidents	Incidents		critical	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
24	assets.view	View Assets	Assets		low	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
25	assets.create	Create Assets	Assets		medium	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
26	assets.update	Update Assets	Assets		medium	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
27	assets.delete	Delete Assets	Assets		high	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
28	vulnerabilities.view	View Vulnerabilities	Vulnerabilities		low	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
29	vulnerabilities.manage	Manage Vulnerabilities	Vulnerabilities		high	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
32	detections.view	View Detection Rules	Detection		low	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
33	detections.create	Create Detection Rules	Detection		medium	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
34	detections.update	Update Detection Rules	Detection		high	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
35	detections.delete	Delete Detection Rules	Detection		critical	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
36	detections.deploy	Deploy Detection Rules	Detection		critical	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
37	reports.view	View Reports	Reports		low	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
38	reports.generate	Generate Reports	Reports		medium	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
39	reports.export	Export Reports	Reports		medium	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
42	apikeys.view	View API Keys	API		medium	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
43	apikeys.create	Create API Keys	API		high	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
44	apikeys.revoke	Revoke API Keys	API		critical	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
45	integrations.view	View Integrations	Integrations		low	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
46	integrations.manage	Manage Integrations	Integrations		high	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
49	compliance.view	View Compliance	Compliance		low	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
50	compliance.manage	Manage Compliance	Compliance		high	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
52	ai.configuration.manage	Manage AI Configuration	AI		critical	2026-08-04 14:37:29.924684	2026-08-04 14:37:29.924684
30	threatintel.view	View Threat Intelligence	Threat Intel		low	2026-08-04 14:37:29.924684	2026-08-05 14:58:31.325752
31	threatintel.manage	Manage Threat Intelligence	Threat Intel		high	2026-08-04 14:37:29.924684	2026-08-05 14:58:31.325752
40	billing.view	View Subscription	Billing		low	2026-08-04 14:37:29.924684	2026-08-05 14:58:31.325752
41	billing.manage	Manage Subscription	Billing		critical	2026-08-04 14:37:29.924684	2026-08-05 14:58:31.325752
47	audit.view	View Audit Logs	Audit		medium	2026-08-04 14:37:29.924684	2026-08-05 14:58:31.325752
48	audit.export	Export Audit Logs	Audit		high	2026-08-04 14:37:29.924684	2026-08-05 14:58:31.325752
51	ai.assistant.use	Use AI Security Assistant	AI		low	2026-08-04 14:37:29.924684	2026-08-05 14:58:31.325752
53	organization.view	View Organization Profile	Organization		low	2026-08-05 14:58:31.325752	2026-08-05 14:58:31.325752
54	organization.update	Update Organization Profile	Organization		high	2026-08-05 14:58:31.325752	2026-08-05 14:58:31.325752
55	security.settings.view	View Security Settings	Security		low	2026-08-05 14:58:31.325752	2026-08-05 14:58:31.325752
56	security.settings.update	Update Security Settings	Security		critical	2026-08-05 14:58:31.325752	2026-08-05 14:58:31.325752
57	access_policies.view	View Access Policies	Access Control		low	2026-08-05 14:58:31.325752	2026-08-05 14:58:31.325752
58	access_policies.manage	Manage Access Policies	Access Control		high	2026-08-05 14:58:31.325752	2026-08-05 14:58:31.325752
59	mfa.view	View MFA Policies	Authentication		low	2026-08-05 14:58:31.325752	2026-08-05 14:58:31.325752
60	mfa.manage	Manage MFA Policies	Authentication		critical	2026-08-05 14:58:31.325752	2026-08-05 14:58:31.325752
61	sessions.view	View Active Sessions	Authentication		low	2026-08-05 14:58:31.325752	2026-08-05 14:58:31.325752
62	sessions.revoke	Revoke User Sessions	Authentication		high	2026-08-05 14:58:31.325752	2026-08-05 14:58:31.325752
63	incidents.assign	Assign Incidents	Incidents		medium	2026-08-05 14:58:31.325752	2026-08-05 14:58:31.325752
64	vulnerabilities.assign	Assign Vulnerabilities	Vulnerabilities		medium	2026-08-05 14:58:31.325752	2026-08-05 14:58:31.325752
65	vulnerabilities.remediate	Remediate Vulnerabilities	Vulnerabilities		high	2026-08-05 14:58:31.325752	2026-08-05 14:58:31.325752
66	detections.analytics.view	View Detection Analytics	Detection		low	2026-08-05 14:58:31.325752	2026-08-05 14:58:31.325752
67	detections.analytics.manage	Manage Detection Analytics	Detection		high	2026-08-05 14:58:31.325752	2026-08-05 14:58:31.325752
68	detections.automation.view	View Detection Automation	Detection		low	2026-08-05 14:58:31.325752	2026-08-05 14:58:31.325752
69	detections.automation.manage	Manage Detection Automation	Detection		high	2026-08-05 14:58:31.325752	2026-08-05 14:58:31.325752
70	forensics.view	View Forensics Cases	Forensics		low	2026-08-05 14:58:31.325752	2026-08-05 14:58:31.325752
71	forensics.manage	Manage Forensics Cases	Forensics		high	2026-08-05 14:58:31.325752	2026-08-05 14:58:31.325752
72	notifications.view	View Notifications	Notifications		low	2026-08-05 14:58:31.325752	2026-08-05 14:58:31.325752
73	notifications.manage	Manage Notification Rules	Notifications		high	2026-08-05 14:58:31.325752	2026-08-05 14:58:31.325752
74	access.policies.view	View Access Policies	Access Control		low	2026-08-05 15:07:01.113218	2026-08-05 15:07:01.113218
75	access.policies.manage	Manage Access Policies	Access Control		high	2026-08-05 15:07:01.113218	2026-08-05 15:07:01.113218
76	detection.analytics.view	View Detection Analytics	Detection		low	2026-08-05 15:07:01.113218	2026-08-05 15:07:01.113218
77	detection.analytics.manage	Manage Detection Analytics	Detection		high	2026-08-05 15:07:01.113218	2026-08-05 15:07:01.113218
78	detection.automation.view	View Detection Automation	Detection		low	2026-08-05 15:07:01.113218	2026-08-05 15:07:01.113218
79	detection.automation.manage	Manage Detection Automation	Detection		high	2026-08-05 15:07:01.113218	2026-08-05 15:07:01.113218
80	security.dashboard.view	View Security Dashboard	Security		low	2026-08-05 15:07:01.113218	2026-08-05 15:07:01.113218
81	security.events.view	View Security Events	Security		low	2026-08-05 15:07:01.113218	2026-08-05 15:07:01.113218
\.


--
-- Data for Name: pkce_attempts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pkce_attempts (attempt_id, tenant_id, code_verifier, created_at) FROM stdin;
vukpOL6xzVdf59V3jAMxCBDty7wbyu53lJqzunhW-kI	BLVCK-CYBER	PHO6bijiWRQ6J0CfaDEwLAva3YLeQmt1sY60xu4fAvIIEKrdVTII-7uSoIQuslzWUfdI2hyB7Uo51su4aMzwIQ	2026-08-03 10:20:18.84372
W7uUgHXgWlOuphG6Egt_8DZ6Vo8AbLOdzxvY61fEHeQ	BLVCK-CYBER	ZSEO0TPgUQXVuChg-7rOufHUdrHEMvkRdBwtKGtEvngBgsOZSZoMRInl0D_0eZ_Lea_QRhh3t91JLwa5htaawQ	2026-08-12 13:56:29.980151
CD6dp0poNPQ9JJmNL5QEZ-nfx2nJ5hgSi-Ox6olsf7I	BLVCK-CYBER	buWiDHkXTJCnyTFZj3IsG7TddBWC93HyKhyvHqgHRbXUMDwH2AJTI1fSJFbCasi_jV2fWDZP2FeBReNJUW8RzQ	2026-08-12 13:57:58.097147
rT0yJq2lByxEDr9omz9h0Vx6AsM_qcvHtzrr2sxx6tQ	BLVCK-CYBER	YyEAXDrDTxrP-XSKzybbZ_n3L7d1e9RdPw2OoZe9p1ak8gZokcGGYZCrDXegZOtfHmLbnQUI1lBHFbBMNzgYXQ	2026-08-12 14:23:50.522169
nVHsvAuGSbTBILIiWgNrsw1Y7bRFMHzrxovd5vMeqZs	BLVCK-CYBER	uAVJrLOVI8pRQM6RSu7D2eJPBW4krv3bFYPfgWTmwxuVVYe285Xlk4YK5yeyCSZkeM8edpbkxjPqmo-tb5Etdw	2026-08-03 14:19:10.352717
FHHy6iZYQ2TNT5H3YwYYNE2pTgcgMmM0FbYovMzkWtg	BLVCK-CYBER	CDiQ7qAUbivupzlNEdCMSf1URKnGqfc0DPMhm0XG0VgsVXPuPFvYyQWuJzaG6PIEhhzuPn25Tq9mSS0Q05zRnA	2026-08-03 14:19:58.764813
dB_D55T6S8uUQ627CFlVjqSy6ug0xDXzv71ZslvbTn8	BLVCK-CYBER	GIzMbEuihPp4PjwgZ-Ox0-Sv-nDgapA-Vv6rAKdYLreMq4maKlvFChMop8-XZTzhk-FJxBahBJdUiZm8v-eh_Q	2026-08-04 08:04:22.497768
N5KPJ7OATOn-GVXsKXBmUq9KKalbOOk__mSPeEIj22g	BLVCK-CYBER	HXfjowTGNN7Wcd8mIpVuuG3QmLxbs3L4dr9J6ylZlQ5l3FMhOMn7yhOrimtpVtHQ2HC8MmLW3e_Ydn0Iwiapqg	2026-08-04 13:23:03.545385
MFow-oZLp1IfSDPqGzrJmTD_0ruqcThX9n0LOgMkRVg	BLVCK-CYBER	UxZDu-5EWpXoSWOfVKQuSzvpPYXMIcE6alOV9JYmTXkBJdsOypdBv36t8lM44sK_R_xvLrr0e18LOEwywEwdug	2026-08-04 13:24:10.593336
AgbkJV8ae2vQLD-nA-R0tvxJo7To5jgyM5jlzxfh_Q0	BLVCK-CYBER	din_WXWH_9JJL_e-bhPeXtziFmMf0HW5VkSFESd_zQQm1gTfrASkWcof79TLT3kYXX9gwpyiuPRR5vDAx4jakg	2026-08-04 13:25:14.863749
m8ApaWt04QQMWfPvxbyeNRs03_cRImc1BGdLMOGKEJA	BLVCK-CYBER	sBrYQzEJXek6wk9FPg77PgehYoJW8tbdYnDi2fp7_VcPi-O37s-ziaiDAgSEsIubVeTFJTx8S6XPfp8N4lrKMg	2026-08-05 08:40:35.209612
mkGaFoD2AR1ZdH231ON5yM-D_74xaSzqVSQy0FGdi-Q	BLVCK-CYBER	qYMAazd0ZUl3pHWfRuwPbH5NddT-A-P6CkFqO2lDwl0SP2ONx5IX-yw9zGyr2MtROpTj0p-ad2zQvJAgu09iiQ	2026-08-06 08:49:51.95952
\.


--
-- Data for Name: role_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.role_permissions (role_key, permission_id) FROM stdin;
OWNER	4
OWNER	5
OWNER	6
OWNER	55
OWNER	56
OWNER	7
OWNER	8
OWNER	9
OWNER	10
OWNER	11
OWNER	12
OWNER	13
OWNER	14
OWNER	59
OWNER	60
OWNER	15
OWNER	16
OWNER	17
OWNER	18
OWNER	19
OWNER	20
OWNER	21
OWNER	22
OWNER	23
OWNER	24
OWNER	25
OWNER	26
OWNER	27
OWNER	28
OWNER	29
OWNER	30
OWNER	31
OWNER	32
OWNER	33
OWNER	34
OWNER	35
OWNER	36
OWNER	70
OWNER	71
OWNER	37
OWNER	38
OWNER	39
OWNER	45
OWNER	46
OWNER	42
OWNER	43
OWNER	44
OWNER	47
OWNER	48
OWNER	49
OWNER	50
OWNER	51
OWNER	52
ADMIN	55
ADMIN	56
ADMIN	59
ADMIN	60
ADMIN	70
ADMIN	71
SOC_MANAGER	55
SOC_MANAGER	59
SOC_MANAGER	30
SOC_MANAGER	31
SOC_MANAGER	70
SOC_MANAGER	71
SOC_MANAGER	49
SOC_ANALYST	30
SOC_ANALYST	70
INCIDENT_RESPONDER	70
VIEWER	32
VIEWER	70
VIEWER	49
OWNER	1
ADMIN	2
ADMIN	3
ADMIN	4
ADMIN	5
ADMIN	7
ADMIN	8
ADMIN	9
ADMIN	10
ADMIN	11
ADMIN	12
ADMIN	13
ADMIN	14
ADMIN	15
ADMIN	16
ADMIN	17
ADMIN	18
ADMIN	19
ADMIN	20
ADMIN	21
ADMIN	22
ADMIN	23
ADMIN	24
ADMIN	25
ADMIN	26
ADMIN	27
ADMIN	28
ADMIN	29
ADMIN	30
ADMIN	31
ADMIN	32
ADMIN	33
ADMIN	34
ADMIN	35
ADMIN	36
ADMIN	37
ADMIN	38
ADMIN	39
ADMIN	42
ADMIN	43
ADMIN	44
ADMIN	45
ADMIN	46
ADMIN	47
ADMIN	48
ADMIN	49
ADMIN	50
ADMIN	51
ADMIN	52
SOC_MANAGER	15
SOC_MANAGER	16
SOC_MANAGER	17
SOC_MANAGER	19
SOC_MANAGER	20
SOC_MANAGER	21
SOC_MANAGER	22
SOC_MANAGER	32
SOC_MANAGER	33
SOC_MANAGER	34
SOC_MANAGER	36
SOC_MANAGER	37
SOC_MANAGER	38
SOC_MANAGER	39
SOC_MANAGER	24
SOC_MANAGER	26
SOC_MANAGER	28
SOC_MANAGER	29
SOC_MANAGER	47
SOC_MANAGER	51
SOC_ANALYST	15
SOC_ANALYST	16
SOC_ANALYST	19
SOC_ANALYST	20
SOC_ANALYST	21
SOC_ANALYST	24
SOC_ANALYST	32
SOC_ANALYST	28
SOC_ANALYST	37
SOC_ANALYST	51
INCIDENT_RESPONDER	15
INCIDENT_RESPONDER	17
INCIDENT_RESPONDER	19
INCIDENT_RESPONDER	21
INCIDENT_RESPONDER	22
INCIDENT_RESPONDER	24
INCIDENT_RESPONDER	37
INCIDENT_RESPONDER	51
VIEWER	15
VIEWER	19
VIEWER	24
VIEWER	37
VIEWER	47
VIEWER	28
VIEWER	30
OWNER	74
OWNER	75
OWNER	76
OWNER	77
OWNER	78
OWNER	79
ADMIN	53
ADMIN	54
ADMIN	74
ADMIN	75
ADMIN	61
ADMIN	62
ADMIN	63
ADMIN	64
ADMIN	65
ADMIN	76
ADMIN	77
ADMIN	78
ADMIN	79
ADMIN	72
ADMIN	73
ADMIN	40
ADMIN	41
SOC_MANAGER	74
SOC_MANAGER	76
SOC_MANAGER	77
SOC_MANAGER	78
SOC_MANAGER	79
SOC_ANALYST	76
\.


--
-- Data for Name: tenant_role_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant_role_permissions (id, tenant_role_id, permission_id) FROM stdin;
1	1	1
2	2	2
3	2	3
4	2	4
5	2	5
6	2	7
7	2	8
8	2	9
9	2	10
10	2	11
11	2	12
12	2	13
13	2	14
14	2	15
15	2	16
16	2	17
17	2	18
18	2	19
19	2	20
20	2	21
21	2	22
22	2	23
23	2	24
24	2	25
25	2	26
26	2	27
27	2	28
28	2	29
29	2	30
30	2	31
31	2	32
32	2	33
33	2	34
34	2	35
35	2	36
36	2	37
37	2	38
38	2	39
39	2	42
40	2	43
41	2	44
42	2	45
43	2	46
44	2	47
45	2	48
46	2	49
47	2	50
48	2	51
49	2	52
50	3	15
51	3	16
52	3	17
53	3	19
54	3	20
55	3	21
56	3	22
57	3	32
58	3	33
59	3	34
60	3	36
61	3	37
62	3	38
63	3	39
64	3	24
65	3	26
66	3	28
67	3	29
68	3	47
69	3	51
70	4	15
71	4	16
72	4	19
73	4	20
74	4	21
75	4	24
76	4	32
77	4	28
78	4	37
79	4	51
80	5	15
81	5	17
82	5	19
83	5	21
84	5	22
85	5	24
86	5	37
87	5	51
88	6	15
89	6	19
90	6	24
91	6	37
92	6	47
93	6	28
94	6	30
95	1	4
96	1	5
97	1	6
98	1	55
99	1	56
100	1	7
101	1	8
102	1	9
103	1	10
104	1	11
105	1	12
106	1	13
107	1	14
108	1	59
109	1	60
110	1	15
111	1	16
112	1	17
113	1	18
114	1	19
115	1	20
116	1	21
117	1	22
118	1	23
119	1	24
120	1	25
121	1	26
122	1	27
123	1	28
124	1	29
125	1	30
126	1	31
127	1	32
128	1	33
129	1	34
130	1	35
131	1	36
132	1	70
133	1	71
134	1	37
135	1	38
136	1	39
137	1	45
138	1	46
139	1	42
140	1	43
141	1	44
142	1	47
143	1	48
144	1	49
145	1	50
146	1	51
147	1	52
148	2	55
149	2	56
150	2	59
151	2	60
152	2	70
153	2	71
154	3	55
155	3	59
156	3	30
157	3	31
158	3	70
159	3	71
160	3	49
161	4	30
162	4	70
163	5	70
164	6	32
165	6	70
166	6	49
167	1	74
168	1	75
169	1	76
170	1	77
171	1	78
172	1	79
173	2	53
174	2	54
175	2	74
176	2	75
177	2	61
178	2	62
179	2	63
180	2	64
181	2	65
182	2	76
183	2	77
184	2	78
185	2	79
186	2	72
187	2	73
188	2	40
189	2	41
190	3	74
191	3	76
192	3	77
193	3	78
194	3	79
195	4	76
\.


--
-- Data for Name: tenant_roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant_roles (id, tenant_id, key, name, description, is_system, is_default, created_at, updated_at) FROM stdin;
1	BLVCK-CYBER	OWNER	Owner	Full tenant ownership with complete access to security operations, administration and configuration.	t	f	2026-08-04 14:45:51.934296	2026-08-05 14:58:31.544462
2	BLVCK-CYBER	ADMIN	Administrator	Customer administrator responsible for users, roles, security settings, integrations and organization management.	t	f	2026-08-04 14:45:51.934296	2026-08-05 14:58:31.544462
3	BLVCK-CYBER	SOC_MANAGER	SOC Manager	Manages security operations, threat monitoring, incidents, investigations and SOC workflows.	t	f	2026-08-04 14:45:51.934296	2026-08-05 14:58:31.544462
4	BLVCK-CYBER	SOC_ANALYST	SOC Analyst	Monitors alerts, investigates threats and performs security analysis.	t	t	2026-08-04 14:45:51.934296	2026-08-05 14:58:31.544462
5	BLVCK-CYBER	INCIDENT_RESPONDER	Incident Responder	Handles incident investigation, containment and response activities.	t	f	2026-08-04 14:45:51.934296	2026-08-05 14:58:31.544462
6	BLVCK-CYBER	VIEWER	Viewer	Read-only access to approved security information and reports.	t	f	2026-08-04 14:45:51.934296	2026-08-05 14:58:31.544462
\.


--
-- Data for Name: tenants; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenants (id, name, slug, created_at, updated_at) FROM stdin;
BLVCK-CYBER	BLVCK CYBER	blvck-cyber	2026-08-03 14:54:41.769116	2026-08-03 14:54:41.769116
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, keycloak_sub, email, name) FROM stdin;
2	f2d0e40a-82b5-4ece-adf1-4f7e96aa395a	ceo@blvckcyber.com	BLVCK CEO
3	236d8565-18c6-4c06-b01b-e83f21f0eca6	admin.test@blvckcyber.com	System Admin Test
4	9725beaf-5f26-4a26-8596-81c86ec3d482	analyst@blvckcyber.com	Security Analyst
5	7142b546-94e5-40f7-a63b-9ff32134598b	viewer@blvckcyber.com	Security Viewer
1	f995d924-925c-4311-9e01-0b7206220c4c	admin@blvckcyber.com	System Administrator
\.


--
-- Name: memberships_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.memberships_id_seq', 14, true);


--
-- Name: permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.permissions_id_seq', 81, true);


--
-- Name: tenant_role_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tenant_role_permissions_id_seq', 195, true);


--
-- Name: tenant_roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tenant_roles_id_seq', 6, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 5, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: memberships memberships_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.memberships
    ADD CONSTRAINT memberships_pkey PRIMARY KEY (id);


--
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (id);


--
-- Name: pkce_attempts pkce_attempts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pkce_attempts
    ADD CONSTRAINT pkce_attempts_pkey PRIMARY KEY (attempt_id);


--
-- Name: role_permissions role_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_pkey PRIMARY KEY (role_key, permission_id);


--
-- Name: tenant_role_permissions tenant_role_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_role_permissions
    ADD CONSTRAINT tenant_role_permissions_pkey PRIMARY KEY (id);


--
-- Name: tenant_roles tenant_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_roles
    ADD CONSTRAINT tenant_roles_pkey PRIMARY KEY (id);


--
-- Name: tenants tenants_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenants
    ADD CONSTRAINT tenants_pkey PRIMARY KEY (id);


--
-- Name: tenant_role_permissions uq_role_permission; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_role_permissions
    ADD CONSTRAINT uq_role_permission UNIQUE (tenant_role_id, permission_id);


--
-- Name: tenant_roles uq_tenant_role_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_roles
    ADD CONSTRAINT uq_tenant_role_key UNIQUE (tenant_id, key);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_membership_user_tenant; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_membership_user_tenant ON public.memberships USING btree (user_id, tenant_id);


--
-- Name: ix_memberships_tenant_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_memberships_tenant_id ON public.memberships USING btree (tenant_id);


--
-- Name: ix_memberships_tenant_role_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_memberships_tenant_role_id ON public.memberships USING btree (tenant_role_id);


--
-- Name: ix_memberships_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_memberships_user_id ON public.memberships USING btree (user_id);


--
-- Name: ix_permissions_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_permissions_key ON public.permissions USING btree (key);


--
-- Name: ix_role_permissions_role; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_role_permissions_role ON public.role_permissions USING btree (role_key);


--
-- Name: ix_tenant_role_permissions_permission_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tenant_role_permissions_permission_id ON public.tenant_role_permissions USING btree (permission_id);


--
-- Name: ix_tenant_role_permissions_tenant_role_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tenant_role_permissions_tenant_role_id ON public.tenant_role_permissions USING btree (tenant_role_id);


--
-- Name: ix_tenant_roles_tenant_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tenant_roles_tenant_id ON public.tenant_roles USING btree (tenant_id);


--
-- Name: ix_tenants_slug; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_tenants_slug ON public.tenants USING btree (slug);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_keycloak_sub; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_keycloak_sub ON public.users USING btree (keycloak_sub);


--
-- Name: memberships fk_membership_tenant; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.memberships
    ADD CONSTRAINT fk_membership_tenant FOREIGN KEY (tenant_id) REFERENCES public.tenants(id) ON DELETE CASCADE;


--
-- Name: memberships fk_membership_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.memberships
    ADD CONSTRAINT fk_membership_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: memberships memberships_tenant_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.memberships
    ADD CONSTRAINT memberships_tenant_role_id_fkey FOREIGN KEY (tenant_role_id) REFERENCES public.tenant_roles(id) ON DELETE CASCADE;


--
-- Name: role_permissions role_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permissions(id) ON DELETE CASCADE;


--
-- Name: tenant_role_permissions tenant_role_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_role_permissions
    ADD CONSTRAINT tenant_role_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permissions(id) ON DELETE CASCADE;


--
-- Name: tenant_role_permissions tenant_role_permissions_tenant_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_role_permissions
    ADD CONSTRAINT tenant_role_permissions_tenant_role_id_fkey FOREIGN KEY (tenant_role_id) REFERENCES public.tenant_roles(id) ON DELETE CASCADE;


--
-- Name: tenant_roles tenant_roles_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_roles
    ADD CONSTRAINT tenant_roles_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict SO815wM4Q7Qmhj6W31jq7e4B13b75eyfoThHxXqPtMr5fRoaMjjmh51AQvh3JCn

