/*
Navicat MySQL Data Transfer

Source Server         : sduoj
Source Server Version : 50647
Source Host           : 192.168.152.128:33306
Source Database       : scmis_new

Target Server Type    : MYSQL
Target Server Version : 50647
File Encoding         : 65001

Date: 2021-02-09 12:53:12
*/

SET FOREIGN_KEY_CHECKS=0;


DROP TABLE IF EXISTS `ms_user_info`;
CREATE TABLE `ms_user_info` (
  `ui_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `ui_username` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名',
  `ui_password` varchar(64) CHARACTER SET utf8 NOT NULL COMMENT '用户密码',
  `ui_name` varchar(32) CHARACTER SET utf8 NOT NULL COMMENT '用户姓名',
  `ui_department` varchar(32) CHARACTER SET utf8 DEFAULT NULL COMMENT '用户学院',
  `ui_major` varchar(32) CHARACTER SET utf8 DEFAULT NULL COMMENT '用户专业',
  `ui_class` varchar(32) CHARACTER SET utf8 DEFAULT NULL COMMENT '班级',
  `ui_role` tinyint(4) NOT NULL DEFAULT '2' COMMENT '用户角色0-管理者1-教师2-学生',
  PRIMARY KEY (`ui_id`) USING BTREE,
  KEY `idx_name` (`ui_name`) USING BTREE,
  KEY `idx_username` (`ui_username`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=COMPACT COMMENT='用户表';


DROP TABLE IF EXISTS `ms_course`;
CREATE TABLE `ms_course` (
  `c_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '开课id',
  `c_version` int(10) NOT NULL DEFAULT 1 COMMENT '乐观锁字段',
  `c_name` varchar(64) CHARACTER SET utf8 NOT NULL COMMENT '课程名称',
  `c_year` smallint(6) NOT NULL COMMENT '开课年份',
  `c_capacity` int(10) NOT NULL COMMENT '课容量',
  `c_teacher_id` bigint(20) NOT NULL COMMENT '教师id',
  `c_period` varchar(2048) CHARACTER SET utf8 NOT NULL COMMENT '上课时间1-16:3-3,2-1,1-8:7-1',
  `c_classroom` varchar(2048) CHARACTER SET utf8 NOT NULL COMMENT '上课地点',
  `c_semester` tinyint(4) NOT NULL COMMENT '开课时间，0是上半年，1是下半年',
  `c_description` varchar(8192) CHARACTER SET utf8mb4 NOT NULL DEFAULT '' COMMENT '课程说明',
  PRIMARY KEY (`c_id`) USING BTREE,
  KEY `idx_teacher_id` (`c_teacher_id`) USING BTREE,
  KEY `idx_name` (`c_name`) USING BTREE,
  CONSTRAINT `c_teacher_id` FOREIGN KEY (`c_teacher_id`) REFERENCES `ms_user_info` (`ui_id`) ON DELETE NO ACTION ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=COMPACT COMMENT='开课表';


DROP TABLE IF EXISTS `ms_course_take`;
CREATE TABLE `ms_course_take` (
  `ct_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '选课id',
  `ct_student_id` bigint(20) NOT NULL COMMENT '学生id',
  `ct_course_id` bigint(20) NOT NULL COMMENT '课程id',
  `ct_grade` int(10) DEFAULT NULL COMMENT '最终成绩, 单位 0.1',
  PRIMARY KEY (`ct_id`) USING BTREE,
  KEY `ct_student_id` (`ct_student_id`) USING BTREE,
  KEY `ct_course_id` (`ct_course_id`) USING BTREE,
  CONSTRAINT `ct_course_id` FOREIGN KEY (`ct_course_id`) REFERENCES `ms_course` (`c_id`) ON DELETE NO ACTION ON UPDATE CASCADE,
  CONSTRAINT `ct_student_id` FOREIGN KEY (`ct_student_id`) REFERENCES `ms_user_info` (`ui_id`) ON DELETE NO ACTION ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=COMPACT COMMENT='选课表';

