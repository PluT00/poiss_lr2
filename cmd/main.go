package main

import (
	"fmt"
	"github.com/google/gopacket"
	"github.com/google/gopacket/layers"
	"github.com/google/gopacket/pcap"
	"log"
	"os/exec"
)

func setupQoS(interfaceName string) error {
	if err := exec.Command("tc", "qdisc", "add", "dev", interfaceName, "root", "handle", "1:", "htb", "default", "30").Run(); err != nil {
		return fmt.Errorf("qdisc add failed: %v", err)
	}
	return nil
}

func applyQoS(trafficType, srcIP, interfaceName string) error {
	switch trafficType {
	case "Voice":
		if err := exec.Command("tc", "class", "add", "dev", interfaceName, "parent", "1:", "classid", "1:1", "htb", "rate", "100kbit", "burst", "10kb").Run(); err != nil {
			log.Printf("Class add for Voice already exists or failed: %v", err)
		}
		if err := exec.Command("tc", "filter", "add", "dev", interfaceName, "protocol", "ip", "prio", "1", "u32", "match", "ip", "src", srcIP, "match", "udp", "dport", "5060", "0xffff", "flowid", "1:1").Run(); err != nil {
			log.Printf("Filter add for Voice already exists or failed: %v", err)
		}
		log.Printf("Applied QoS for Voice from %s on %s", srcIP, interfaceName)
	case "Video":
		if err := exec.Command("tc", "class", "add", "dev", interfaceName, "parent", "1:", "classid", "1:2", "htb", "rate", "1mbit", "burst", "20kb").Run(); err != nil {
			log.Printf("Class add for Video already exists or failed: %v", err)
		}
		if err := exec.Command("tc", "filter", "add", "dev", interfaceName, "protocol", "ip", "prio", "2", "u32", "match", "ip", "src", srcIP, "match", "udp", "dport", "1935", "0xffff", "flowid", "1:2").Run(); err != nil {
			log.Printf("Filter add for Video already exists or failed: %v", err)
		}
		log.Printf("Applied QoS for Video from %s on %s", srcIP, interfaceName)
	case "Data":
		if err := exec.Command("tc", "class", "add", "dev", interfaceName, "parent", "1:", "classid", "1:3", "htb", "rate", "500kbit", "burst", "15kb").Run(); err != nil {
			log.Printf("Class add for Data already exists or failed: %v", err)
		}
		if err := exec.Command("tc", "filter", "add", "dev", interfaceName, "protocol", "ip", "prio", "3", "u32", "match", "ip", "src", srcIP, "match", "udp", "dport", "80", "0xffff", "flowid", "1:3").Run(); err != nil {
			log.Printf("Filter add for Data already exists or failed: %v", err)
		}
		log.Printf("Applied QoS for Data from %s on %s", srcIP, interfaceName)
	}
	return nil
}

func classifyTraffic(packet gopacket.Packet) {
	if ipLayer := packet.Layer(layers.LayerTypeIPv4); ipLayer != nil {
		ip, _ := ipLayer.(*layers.IPv4)
		srcIP := ip.SrcIP.String()

		if transportLayer := packet.TransportLayer(); transportLayer != nil {
			switch t := transportLayer.(type) {
			case *layers.UDP:
				srcPort := t.SrcPort
				dstPort := t.DstPort
				switch {
				case srcPort == 5060 || dstPort == 5060:
					if err := applyQoS("Voice", srcIP, "r2-eth1"); err != nil {
						log.Printf("QoS error for Voice: %v", err)
					}
				case srcPort == 1935 || dstPort == 1935:
					if err := applyQoS("Video", srcIP, "r2-eth1"); err != nil {
						log.Printf("QoS error for Video: %v", err)
					}
				case srcPort == 80 || dstPort == 80:
					if err := applyQoS("Data", srcIP, "r2-eth1"); err != nil {
						log.Printf("QoS error for Data: %v", err)
					}
				}
			default:
				return
			}
		}
	}
}

func main() {
	handle, err := pcap.OpenLive("r2-eth1", 1024, false, pcap.BlockForever)
	if err != nil {
		log.Fatal("Error opening interface:", err)
	}
	defer handle.Close()

	if err := setupQoS("r2-eth1"); err != nil {
		log.Fatal("QoS setup failed:", err)
	}

	packetSource := gopacket.NewPacketSource(handle, handle.LinkType())
	log.Println("Starting traffic capture on r2-eth1...")

	for packet := range packetSource.Packets() {
		classifyTraffic(packet)
	}
}
