#include "net_stack.h"
#include "../drivers/rtl8139.h"

static int ip_eq4(const uint8_t a[4], const uint8_t b[4]){ for(int i=0;i<4;i++) if(a[i]!=b[i]) return 0; return 1; }

void net_handle_packet(uint8_t *buffer, uint32_t length){
    if(!buffer||length<sizeof(eth_hdr_t)) return;
    eth_hdr_t *eth=(eth_hdr_t*)buffer;
    uint16_t et=ntohs(eth->type);

    if(et==0x0806 && length>=sizeof(eth_hdr_t)+sizeof(arp_hdr_t)){
        arp_hdr_t *arp=(arp_hdr_t*)(buffer+sizeof(eth_hdr_t));
        if(ntohs(arp->oper)==1 && ip_eq4(arp->tpa,g_net_ip)){
            uint8_t out[sizeof(eth_hdr_t)+sizeof(arp_hdr_t)];
            eth_hdr_t *re=(eth_hdr_t*)out; arp_hdr_t *ra=(arp_hdr_t*)(out+sizeof(eth_hdr_t));
            for(int i=0;i<6;i++){ re->dst[i]=eth->src[i]; re->src[i]=g_net_mac[i]; ra->tha[i]=arp->sha[i]; ra->sha[i]=g_net_mac[i]; }
            re->type=htons(0x0806); ra->htype=htons(1); ra->ptype=htons(0x0800); ra->hlen=6; ra->plen=4; ra->oper=htons(2);
            for(int i=0;i<4;i++){ ra->spa[i]=g_net_ip[i]; ra->tpa[i]=arp->spa[i]; }
            rtl8139_send_packet(out,sizeof(out));
        }
        return;
    }

    if(et==0x0800 && length>=sizeof(eth_hdr_t)+sizeof(ip_hdr_t)+sizeof(icmp_echo_t)){
        ip_hdr_t *ip=(ip_hdr_t*)(buffer+sizeof(eth_hdr_t));
        uint8_t ihl=(ip->ver_ihl&0x0F)*4;
        if(ip->proto==1 && length>=sizeof(eth_hdr_t)+ihl+sizeof(icmp_echo_t)){
            icmp_echo_t *icmp=(icmp_echo_t*)((uint8_t*)ip+ihl);
            if(icmp->type==8 && ip_eq4((uint8_t*)&ip->dst_ip,g_net_ip)){
                uint8_t out[1518]; uint32_t plen=length;
                for(uint32_t i=0;i<plen;i++) out[i]=buffer[i];
                eth_hdr_t *oe=(eth_hdr_t*)out; ip_hdr_t *oi=(ip_hdr_t*)(out+sizeof(eth_hdr_t)); icmp_echo_t *oc=(icmp_echo_t*)((uint8_t*)oi+ihl);
                for(int i=0;i<6;i++){ uint8_t t=oe->src[i]; oe->src[i]=oe->dst[i]; oe->dst[i]=t; }
                uint32_t tip=oi->src_ip; oi->src_ip=oi->dst_ip; oi->dst_ip=tip;
                oc->type=0; oc->checksum=0;
                uint16_t icmp_len=ntohs(oi->total_len)-ihl;
                oc->checksum=net_checksum16(oc,icmp_len);
                oi->check=0; oi->check=net_checksum16(oi,ihl);
                rtl8139_send_packet(out,plen);
            }
        }
    }
}
