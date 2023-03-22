NetBSD 9.3 remote overflow
```
nfs_namei(struct nameidata *ndp, nfsrvfh_t *nsfh, uint32_t len, struct nfssvc_sock *slp, struct mbuf *nam, struct mbuf **mdp, char **dposp, struct vnode **retdirp, int *dirattr_retp, struct vattr *dirattrp, struct lwp *l, int kerbflag, int pubflag)
{
        int i, rem;
        struct mbuf *md;
        char *fromcp, *tocp, *cp, *path;
        struct vnode *dp;
        int error, rdonly;
        int neverfollow;
        struct componentname *cnp = &ndp->ni_cnd;

        *retdirp = NULL;
        ndp->ni_pathbuf = NULL;

[1]        if ((len + 1) > NFS_MAXPATHLEN)
                return (ENAMETOOLONG);
        if (len == 0)
                return (EACCES);
		...

	 	path = PNBUF_GET();
        fromcp = *dposp;
        tocp = path;
        md = *mdp;
        rem = mtod(md, char *) + md->m_len - fromcp;
        for (i = 0; i < len; i++) {
                while (rem == 0) {
                        md = md->m_next;
                        if (md == NULL) {
                                error = EBADRPC;
                                goto out;
                        }
                        fromcp = mtod(md, void *);
                        rem = md->m_len;
                }
                if (*fromcp == '\0' || (!pubflag && *fromcp == '/')) {
                        error = EACCES;
                        goto out;
                }
                *tocp++ = *fromcp++;
                rem--;
        }

}
```

if len equals to (unsigned)-1, check on line #1 could be bypassed.

It leads to heap overflow in 'for' loop.

How we supply negative len to nfs_namei() ?

```
int
nfsrv_remove(struct nfsrv_descript *nfsd, struct nfssvc_sock *slp, struct lwp *lwp, struct mbuf **mrq)
{
   	int len; 
	...
		nfsm_srvmtofh(&nsfh);
        nfsm_srvnamesiz(len);
        nd.ni_cnd.cn_cred = cred;
        nd.ni_cnd.cn_nameiop = DELETE;
        nd.ni_cnd.cn_flags = LOCKPARENT | LOCKLEAF;
        error = nfs_namei(&nd, &nsfh, len, slp, nam, &md, &dpos,
                &dirp, (v3 ? &dirfor_ret : NULL), &dirfor,
                lwp, (nfsd->nd_flag & ND_KERBAUTH), false);
	...
}

#define nfsm_srvnamesiz(s) \
                { nfsm_dissect(tl,uint32_t *,NFSX_UNSIGNED); \
                if (((s) = fxdr_unsigned(uint32_t,*tl)) > NFS_MAXNAMLEN) \
                        error = NFSERR_NAMETOL; \
                if (error) \
                        nfsm_reply(0); \
                }

```

'len' is signed, so nfsm_srvnamesiz checks could by bypassed.

How to verify:
1. setup nfs/mountd
2. run t2.py



